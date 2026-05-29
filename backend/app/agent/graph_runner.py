"""LangGraph-backed agent runner for chat workflows."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, StateGraph

from app.agent.bootstrap import create_tool_registry
from app.agent.intent_classifier import classify_intent, normalize_query
from app.agent.state import PaperAgentState
from app.agent.tool_registry import ToolRegistry
from app.core.config import settings
from app.core.logging import logger
from app.schemas.chat import ChatResponse, PaperCardItem
from app.services.memory_service import SemanticMemoryService, ShortTermMemoryService
from app.tools.arxiv_tool import ArxivTool
from app.tools.llm_client import llm_client
from app.tools.report_tool import ReportTool
from app.tools.rerank_tool import RerankTool
from app.tools.trace_tool import TraceTool

MAX_REACT_STEPS = 6


class LangGraphAgentRunner:
    """Runs fixed business subgraphs and a controlled ReAct subgraph."""

    def __init__(
        self,
        trace_tool: TraceTool | None = None,
        use_react: bool | None = None,
    ):
        self.trace_tool = trace_tool or TraceTool()
        self.use_react = settings.use_react_agent if use_react is None else use_react

        self.arxiv_tool = ArxivTool()
        self.rerank_tool = RerankTool()
        self.report_tool = ReportTool()
        self.tool_registry: ToolRegistry = create_tool_registry()
        self.short_memory = ShortTermMemoryService()
        self.semantic_memory = SemanticMemoryService()

        self._graph = None
        self._checkpointer: AsyncSqliteSaver | None = None
        self._checkpoint_conn: aiosqlite.Connection | None = None

    async def run_chat(self, message: str, session_id: str) -> ChatResponse:
        """Run the chat task through the LangGraph StateGraph."""
        await self.short_memory.add_user_message(session_id, message)
        messages = await self.short_memory.load_messages(session_id)
        conversation_summary = await self.short_memory.build_context_summary(session_id)
        last_papers = await self.short_memory.get_last_papers(session_id)
        user_preferences = await self.semantic_memory.load_user_preferences()
        interest_query = await self.semantic_memory.infer_interest_query(session_id)
        long_term_memories = await self.semantic_memory.retrieve(
            query=message,
            session_id=session_id,
            top_k=5,
        )

        trace = self.trace_tool.create(
            task_type="chat",
            user_input=message,
            tags=["langgraph"],
        )
        graph = await self._get_graph()
        config = {"configurable": {"thread_id": trace.trace_id}}

        initial_state: PaperAgentState = {
            "trace_id": trace.trace_id,
            "session_id": session_id,
            "user_message": message,
            "status": "running",
            "step_count": 0,
            "max_steps": MAX_REACT_STEPS,
            "observations": [],
            "messages": messages,
            "conversation_summary": conversation_summary,
            "last_papers": last_papers,
            "long_term_memories": long_term_memories,
            "user_preferences": user_preferences,
            "interest_query": interest_query,
        }

        try:
            final_state = await graph.ainvoke(initial_state, config=config)
            final_response = final_state.get("final_response", {})
            status = final_state.get("status", "success")
            error = final_state.get("error", "")
            await self.trace_tool.complete(
                trace.trace_id,
                status="failed" if status == "failed" else "success",
                error_message=error,
                trace=trace,
            )
            chat_response = self._to_chat_response(final_response, trace.trace_id)
            await self._persist_memory_after_run(session_id, message, trace.trace_id, final_state, chat_response)
            return chat_response
        except Exception as exc:
            logger.error(f"LangGraph chat run failed: {exc}")
            await self.trace_tool.complete(
                trace.trace_id,
                status="failed",
                error_message=str(exc),
                trace=trace,
            )
            await self.short_memory.add_assistant_message(
                session_id,
                f"Task failed: {exc}",
                metadata={"trace_id": trace.trace_id, "response_type": "error"},
            )
            return ChatResponse(
                success=False,
                type="error",
                trace_id=trace.trace_id,
                message=f"任务执行失败: {exc}",
                papers=[],
            )

    async def get_state_history(self, trace_id: str) -> list[Any]:
        """Return LangGraph checkpoint snapshots for a trace/thread."""
        graph = await self._get_graph()
        config = {"configurable": {"thread_id": trace_id}}
        snapshots = []
        async for snapshot in graph.aget_state_history(config):
            snapshots.append(snapshot)
        return snapshots

    async def close(self) -> None:
        if self._checkpoint_conn:
            await self._checkpoint_conn.close()
            self._checkpoint_conn = None
            self._checkpointer = None
            self._graph = None

    async def _get_graph(self):
        if self._graph is not None:
            return self._graph

        checkpoint_path = settings.langgraph_checkpoint_db
        checkpoint_dir = os.path.dirname(checkpoint_path)
        if checkpoint_dir:
            os.makedirs(checkpoint_dir, exist_ok=True)

        self._checkpoint_conn = await aiosqlite.connect(checkpoint_path)
        self._checkpointer = AsyncSqliteSaver(self._checkpoint_conn)
        await self._checkpointer.setup()
        self._graph = self._build_graph().compile(
            checkpointer=self._checkpointer,
            name="research_agent_graph",
        )
        return self._graph

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(PaperAgentState)

        graph.add_node("classify_intent", self._classify_intent_node)
        graph.add_node("query_normalize", self._query_normalize_node)
        graph.add_node("arxiv_search", self._arxiv_search_node)
        graph.add_node("paper_rerank", self._paper_rerank_node)
        graph.add_node("card_summary", self._card_summary_node)
        graph.add_node("build_paper_response", self._build_paper_response_node)
        graph.add_node("general_chat", self._general_chat_node)
        graph.add_node("unsupported", self._unsupported_node)

        graph.add_node("react_plan", self._react_plan_node)
        graph.add_node("react_tool_guard", self._react_tool_guard_node)
        graph.add_node("react_tool_execute", self._react_tool_execute_node)
        graph.add_node("react_observe", self._react_observe_node)
        graph.add_node("react_final_response", self._react_final_response_node)
        graph.add_node("react_fail_response", self._react_fail_response_node)

        graph.add_edge(START, "classify_intent")
        graph.add_conditional_edges(
            "classify_intent",
            self._route_after_intent,
            {
                "paper_search_fixed": "query_normalize",
                "paper_search_react": "react_plan",
                "general_chat": "general_chat",
                "unsupported": "unsupported",
            },
        )

        graph.add_edge("query_normalize", "arxiv_search")
        graph.add_conditional_edges(
            "arxiv_search",
            self._route_after_search,
            {
                "rerank": "paper_rerank",
                "final": "build_paper_response",
            },
        )
        graph.add_edge("paper_rerank", "card_summary")
        graph.add_edge("card_summary", "build_paper_response")
        graph.add_edge("build_paper_response", END)
        graph.add_edge("general_chat", END)
        graph.add_edge("unsupported", END)

        graph.add_conditional_edges(
            "react_plan",
            self._route_after_react_plan,
            {
                "guard": "react_tool_guard",
                "final": "react_final_response",
            },
        )
        graph.add_conditional_edges(
            "react_tool_guard",
            self._route_after_tool_guard,
            {
                "execute": "react_tool_execute",
                "fail": "react_fail_response",
            },
        )
        graph.add_edge("react_tool_execute", "react_observe")
        graph.add_conditional_edges(
            "react_observe",
            self._route_after_react_observe,
            {
                "continue": "react_plan",
                "final": "react_final_response",
                "fail": "react_fail_response",
            },
        )
        graph.add_edge("react_final_response", END)
        graph.add_edge("react_fail_response", END)

        return graph

    async def _classify_intent_node(self, state: PaperAgentState) -> dict:
        message = state.get("user_message", "")
        intent_result = classify_intent(message)
        entities = intent_result.get("entities", {})
        raw_topic = entities.get("topic", "")
        explicit_topic = self._extract_topic_from_message(message)
        if explicit_topic:
            raw_topic = explicit_topic
            entities["topic"] = raw_topic

        if intent_result.get("intent") != "paper_search" and self._is_paper_search_request(message):
            intent_result = {"intent": "paper_search", "confidence": 0.8, "entities": entities}

        # Detect new intents that the keyword classifier might miss
        intent_result = self._refine_intent(message, intent_result, state)

        referenced_paper = self._select_referenced_paper(message, state.get("last_papers", []))
        if referenced_paper:
            entities["referenced_arxiv_id"] = referenced_paper.get("arxiv_id", "")
            if self._asks_for_similar_papers(message):
                intent_result = {"intent": "paper_search", "confidence": 0.85, "entities": entities}
                raw_topic = self._paper_memory_query(referenced_paper)
            elif self._asks_for_deep_read(message):
                intent_result = {"intent": "paper_deep_read", "confidence": 0.90, "entities": entities}
                entities["arxiv_id"] = referenced_paper.get("arxiv_id", "")

        if self._is_interest_search(message) and (not raw_topic or self._looks_like_interest_placeholder(raw_topic)):
            intent_result = {"intent": "interest_recommendation", "confidence": 0.90, "entities": entities}
            raw_topic = state.get("interest_query") or "machine learning"
            entities["topic"] = raw_topic

        normalized = normalize_query(raw_topic) if raw_topic else ""
        intent = intent_result.get("intent", "unsupported")

        # Map intent to skill
        skill_map = {
            "paper_deep_read": "paper_deep_read_skill",
            "paper_compare": "paper_compare_skill",
            "literature_survey": "literature_survey_skill",
            "interest_recommendation": "interest_recommendation_skill",
            "memory_profile": "memory_profile_skill",
            "trace_diagnosis": "trace_diagnosis_skill",
            "paper_search": "paper_search_card_skill",
        }
        selected_skill = skill_map.get(intent, "")

        # Build slots
        slots = {
            "topic": raw_topic,
            "paper_ref": entities.get("referenced_arxiv_id", ""),
            "top_n": entities.get("top_n", 2),
            "candidate_k": entities.get("candidate_k", 20),
            "arxiv_ids": entities.get("arxiv_ids", []),
            "arxiv_id": entities.get("arxiv_id", ""),
            "action": entities.get("action", "read"),
        }

        # Clarification check
        needs_clarification = False
        clarification_question = ""
        if intent not in ("general_chat", "unsupported", "memory_profile", "trace_diagnosis"):
            if not raw_topic and not referenced_paper and not entities.get("arxiv_id"):
                if intent in ("paper_search", "literature_survey", "interest_recommendation", "paper_deep_read", "paper_compare"):
                    needs_clarification = True
                    clarification_question = "请问您想搜索什么方向的论文？"

        return {
            "current_node": "classify_intent",
            "intent_result": intent_result,
            "intent": intent,
            "entities": entities,
            "query": raw_topic,
            "normalized_query": normalized,
            "referenced_paper": referenced_paper or {},
            "candidate_k": entities.get("candidate_k", 20),
            "top_n": entities.get("top_n", 2),
            "original_query": message,
            "rewritten_query": normalized,
            "query_rewrite_source": "explicit_user_topic" if raw_topic else "",
            "query_filters": entities.get("query_filters", {}),
            "selected_skill": selected_skill,
            "slots": slots,
            "needs_clarification": needs_clarification,
            "clarification_question": clarification_question,
            "status": "running",
        }

    async def _query_normalize_node(self, state: PaperAgentState) -> dict:
        raw_topic = state.get("query") or state.get("entities", {}).get("topic", "")
        normalized = normalize_query(raw_topic) if raw_topic else "machine learning"
        return {
            "current_node": "query_normalize",
            "normalized_query": normalized,
            "candidate_k": state.get("candidate_k", 20),
            "top_n": state.get("top_n", 2),
        }

    async def _arxiv_search_node(self, state: PaperAgentState) -> dict:
        query = state.get("normalized_query") or "machine learning"
        result = await self.arxiv_tool.search(
            query=query,
            max_results=state.get("candidate_k", 20),
        )
        if not result.get("success"):
            return {
                "current_node": "arxiv_search",
                "candidate_papers": [],
                "status": "failed",
                "error": result.get("error", "ARXIV_SEARCH_FAILED"),
            }
        return {
            "current_node": "arxiv_search",
            "candidate_papers": result.get("papers", []),
            "status": "running",
        }

    async def _paper_rerank_node(self, state: PaperAgentState) -> dict:
        result = await self.rerank_tool.rerank(
            query=state.get("normalized_query", ""),
            papers=state.get("candidate_papers", []),
            top_n=state.get("top_n", 2),
            user_preferences=state.get("user_preferences", {}),
        )
        if not result.get("success"):
            return {
                "current_node": "paper_rerank",
                "reranked_papers": state.get("candidate_papers", [])[: state.get("top_n", 2)],
                "status": "running",
                "error": result.get("error", ""),
            }
        return {
            "current_node": "paper_rerank",
            "reranked_papers": result.get("ranked_papers", []),
            "status": "running",
        }

    async def _card_summary_node(self, state: PaperAgentState) -> dict:
        papers = list(state.get("reranked_papers", []))
        query = state.get("normalized_query", "")
        for paper in papers:
            try:
                summary_result = await self.report_tool.generate_card_summary(
                    paper=paper,
                    query=query,
                )
                if summary_result.get("success") and summary_result.get("summary"):
                    summary = summary_result["summary"]
                    paper["summary"] = summary.get("summary", paper.get("abstract", ""))
                    paper["core_problem"] = summary.get("core_problem", "")
                    paper["method"] = summary.get("method", "")
                    paper["result"] = summary.get("result", "")
                    paper["summary_source"] = summary.get("summary_source", "metadata_only")
            except Exception as exc:
                logger.warning(f"Card summary failed for {paper.get('arxiv_id')}: {exc}")
        return {
            "current_node": "card_summary",
            "selected_papers": papers,
            "papers": papers,
            "status": "running",
        }

    async def _build_paper_response_node(self, state: PaperAgentState) -> dict:
        query = state.get("normalized_query") or state.get("query") or "machine learning"
        papers = state.get("selected_papers") or state.get("candidate_papers", [])
        card_items = self._build_paper_cards(papers, query)
        if not card_items:
            message = f'未找到与 "{query}" 相关的论文，请尝试其他关键词。'
        else:
            message = f"找到 {len(card_items)} 篇关于 {query} 的论文"
        return {
            "current_node": "build_paper_response",
            "status": "success",
            "final_response": {
                "success": True,
                "type": "paper_search_result",
                "trace_id": state.get("trace_id", ""),
                "message": message,
                "papers": [p.model_dump() for p in card_items],
            },
        }

    async def _general_chat_node(self, state: PaperAgentState) -> dict:
        if state.get("needs_clarification"):
            question = state.get("clarification_question", "请问您需要什么帮助？")
            return {
                "current_node": "general_chat",
                "status": "success",
                "final_response": {
                    "success": True,
                    "type": "clarification",
                    "trace_id": state.get("trace_id", ""),
                    "message": question,
                    "papers": [],
                },
            }

        referenced_paper = state.get("referenced_paper") or {}
        if referenced_paper:
            authors = referenced_paper.get("authors", [])
            if isinstance(authors, list):
                authors_text = ", ".join(authors[:3])
            else:
                authors_text = str(authors)
            summary = referenced_paper.get("summary") or referenced_paper.get("abstract", "")
            message = (
                f"Previous paper: {referenced_paper.get('title', '')}\n"
                f"Authors: {authors_text}\n"
                f"arXiv: {referenced_paper.get('arxiv_id', '')}\n"
                f"Summary: {summary[:800]}"
            )
            return {
                "current_node": "general_chat",
                "status": "success",
                "final_response": {
                    "success": True,
                    "type": "general_chat",
                    "trace_id": state.get("trace_id", ""),
                    "message": message,
                    "papers": [],
                },
            }

        return {
            "current_node": "general_chat",
            "status": "success",
            "final_response": {
                "success": True,
                "type": "general_chat",
                "trace_id": state.get("trace_id", ""),
                "message": (
                    "你好，我是 arXiv 论文助手。你可以输入研究方向搜索论文，"
                    "例如：给我找 2 篇关于 agent 的论文。"
                ),
                "papers": [],
            },
        }

    async def _unsupported_node(self, state: PaperAgentState) -> dict:
        intent = state.get("intent", "unsupported")
        return {
            "current_node": "unsupported",
            "status": "success",
            "final_response": {
                "success": True,
                "type": "unsupported",
                "trace_id": state.get("trace_id", ""),
                "message": f"意图识别为 {intent}，当前 LangGraph 路径优先支持论文搜索。",
                "papers": [],
            },
        }

    async def _react_plan_node(self, state: PaperAgentState) -> dict:
        step_count = state.get("step_count", 0) + 1
        intent = state.get("intent", "paper_search")
        tools = self._react_tools(intent)
        tool_schemas = [tool.schema for tool in tools]

        if not llm_client.available:
            return self._fallback_react_plan(state, step_count)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a controlled ReAct agent for an arXiv research assistant. Choose one available tool "
                    "or answer directly when the task is complete. Prefer high-level skills over atomic tools. "
                    "Never parse full text during search. Skill mapping: "
                    "paper_deep_read -> paper_deep_read_skill, "
                    "paper_compare -> paper_compare_skill, "
                    "literature_survey -> literature_survey_skill, "
                    "interest_recommendation -> interest_recommendation_skill, "
                    "memory_profile -> memory_profile_skill, "
                    "trace_diagnosis -> trace_diagnosis_skill, "
                    "paper_search -> paper_search_card_skill."
                ),
            },
            {
                "role": "user",
                "content": self._react_prompt(state),
            },
        ]
        result = await llm_client.chat_with_tools(
            messages=messages,
            tools=tool_schemas,
            temperature=0.2,
            max_tokens=1024,
        )
        if result.get("success") and result.get("tool_calls"):
            call = result["tool_calls"][0]
            function = call.get("function", {})
            tool_name = function.get("name", "")
            arguments = self._parse_tool_arguments(function.get("arguments", "{}"))
            if tool_name and tool_name != "final_answer":
                group_id = self._tool_group_id(state, step_count)
                await self.short_memory.add_tool_call(
                    session_id=state.get("session_id", ""),
                    group_id=group_id,
                    tool_call_id=group_id,
                    tool_name=tool_name,
                    arguments=arguments,
                )
            return {
                "current_node": "react_plan",
                "step_count": step_count,
                "selected_tool": tool_name,
                "tool_arguments": arguments,
                "reasoning_summary": result.get("content") or f"选择调用 {tool_name}",
                "status": "running",
            }

        plan = await llm_client.plan_with_tools(
            user_message=state.get("user_message", ""),
            state_summary=self._state_summary(state),
            tools=tool_schemas,
        )
        tool_name = plan.get("action", "final_answer")
        if tool_name != "final_answer":
            group_id = self._tool_group_id(state, step_count)
            await self.short_memory.add_tool_call(
                session_id=state.get("session_id", ""),
                group_id=group_id,
                tool_call_id=group_id,
                tool_name=tool_name,
                arguments=plan.get("arguments", {}),
            )
        return {
            "current_node": "react_plan",
            "step_count": step_count,
            "selected_tool": tool_name,
            "tool_arguments": plan.get("arguments", {}),
            "reasoning_summary": plan.get("reasoning_summary", ""),
            "status": "running" if plan.get("success") else "failed",
            "error": plan.get("error", ""),
        }

    async def _react_tool_guard_node(self, state: PaperAgentState) -> dict:
        tool_name = state.get("selected_tool", "")
        validation = self.tool_registry.validate_call(
            name=tool_name,
            context={
                "intent": state.get("intent", ""),
                "step": state.get("step_count", 0),
                "react": True,
            },
        )
        if not validation.get("success"):
            return {
                "current_node": "react_tool_guard",
                "status": "failed",
                "error": validation.get("message", "TOOL_NOT_ALLOWED"),
                "tool_observation": validation,
            }
        return {
            "current_node": "react_tool_guard",
            "status": "running",
        }

    async def _react_tool_execute_node(self, state: PaperAgentState) -> dict:
        observation = await self.tool_registry.call(
            name=state.get("selected_tool", ""),
            arguments=state.get("tool_arguments", {}),
            context={
                "intent": state.get("intent", ""),
                "step": state.get("step_count", 0),
                "react": True,
            },
        )
        group_id = self._tool_group_id(state, state.get("step_count", 0))
        await self.short_memory.add_tool_response(
            session_id=state.get("session_id", ""),
            group_id=group_id,
            tool_call_id=group_id,
            tool_name=state.get("selected_tool", ""),
            response=observation,
        )
        return {
            "current_node": "react_tool_execute",
            "tool_observation": observation,
            "status": "running" if observation.get("success") else "failed",
            "error": observation.get("error") or observation.get("detail", ""),
        }

    async def _react_observe_node(self, state: PaperAgentState) -> dict:
        observations = list(state.get("observations", []))
        observation = state.get("tool_observation", {})
        observations.append(observation)
        update: dict[str, Any] = {
            "current_node": "react_observe",
            "observations": observations,
            "status": "running" if observation.get("success") else "failed",
        }
        if observation.get("papers"):
            update["papers"] = observation["papers"]
            update["selected_papers"] = observation["papers"]
        elif observation.get("ranked_papers"):
            update["papers"] = observation["ranked_papers"]
            update["selected_papers"] = observation["ranked_papers"]
        if observation.get("report_markdown"):
            update["report_markdown"] = observation["report_markdown"]
        if observation.get("comparison"):
            update["comparison"] = observation["comparison"]
        if observation.get("survey_markdown"):
            update["survey_markdown"] = observation["survey_markdown"]
        if observation.get("preferences"):
            update["user_preferences"] = observation["preferences"]
        if observation.get("traces"):
            update["papers"] = []  # trace diagnosis doesn't produce papers
        return update

    async def _react_final_response_node(self, state: PaperAgentState) -> dict:
        intent = state.get("intent", "paper_search")
        papers = self._dedupe_papers(state.get("papers", []))
        card_items = self._build_paper_cards(papers, state.get("normalized_query", ""))
        message = state.get("reasoning_summary") or "任务已完成"

        # Build response type and message based on intent
        if intent == "paper_deep_read":
            response_type = "deep_read_result"
            arxiv_id = state.get("slots", {}).get("arxiv_id", "")
            report_summary = (state.get("report_markdown", "") or "")[:500]
            message = f"论文 {arxiv_id} 精读报告已生成" if arxiv_id else "精读报告已生成"
            if report_summary:
                message = report_summary
        elif intent == "paper_compare":
            response_type = "comparison_result"
            comparison = state.get("comparison", {})
            overview = comparison.get("overview", "")
            message = overview or "论文对比分析已完成"
        elif intent == "literature_survey":
            response_type = "survey_result"
            survey_md = state.get("survey_markdown", "")
            message = survey_md[:300] if survey_md else "文献综述已生成"
        elif intent == "memory_profile":
            response_type = "memory_profile_result"
            prefs = state.get("user_preferences", {})
            topics = prefs.get("preferred_topics", [])
            message = f"偏好已更新: {', '.join(topics[:5])}" if topics else "偏好设置已更新"
        elif intent == "trace_diagnosis":
            response_type = "trace_diagnosis_result"
            observations = state.get("observations", [])
            if observations:
                last_obs = observations[-1]
                message = last_obs.get("message", "追踪诊断完成")
            else:
                message = "追踪诊断完成"
        elif card_items:
            response_type = "paper_search_result"
            message = f"找到 {len(card_items)} 篇相关论文"
        else:
            response_type = "chat_result"
            message = "任务已完成"

        return {
            "current_node": "react_final_response",
            "status": "success",
            "final_response": {
                "success": True,
                "type": response_type,
                "trace_id": state.get("trace_id", ""),
                "message": message,
                "papers": [p.model_dump() for p in card_items],
            },
        }

    async def _react_fail_response_node(self, state: PaperAgentState) -> dict:
        error = state.get("error") or "ReAct tool execution failed"
        return {
            "current_node": "react_fail_response",
            "status": "failed",
            "final_response": {
                "success": False,
                "type": "error",
                "trace_id": state.get("trace_id", ""),
                "message": error,
                "papers": [],
            },
        }

    def _route_after_intent(self, state: PaperAgentState) -> str:
        if state.get("needs_clarification"):
            return "general_chat"

        intent = state.get("intent", "unsupported")
        if intent == "paper_search":
            return "paper_search_react" if self.use_react else "paper_search_fixed"
        if intent == "general_chat":
            return "general_chat"
        if intent == "unsupported":
            return "unsupported"

        # All new intents route through ReAct (which selects the right skill)
        react_intents = {
            "paper_deep_read", "paper_compare", "literature_survey",
            "interest_recommendation", "memory_profile", "trace_diagnosis",
            "paper_collect", "paper_parse", "library_search", "report_view",
            "trace_search",
        }
        if intent in react_intents:
            return "paper_search_react"

        return "unsupported"

    def _route_after_search(self, state: PaperAgentState) -> str:
        if state.get("status") == "failed":
            return "final"
        return "rerank" if state.get("candidate_papers") else "final"

    def _route_after_react_plan(self, state: PaperAgentState) -> str:
        if state.get("selected_tool") == "final_answer":
            return "final"
        if state.get("status") == "failed" and not state.get("selected_tool"):
            return "final"
        return "guard"

    def _route_after_tool_guard(self, state: PaperAgentState) -> str:
        return "fail" if state.get("status") == "failed" else "execute"

    def _route_after_react_observe(self, state: PaperAgentState) -> str:
        if state.get("status") == "failed":
            return "fail"
        if state.get("papers") or state.get("step_count", 0) >= state.get("max_steps", MAX_REACT_STEPS):
            return "final"
        return "continue"

    def _react_tools(self, intent: str):
        tools = self.tool_registry.list_tools(intent)
        skill_tools = [tool for tool in tools if tool.name.endswith("_skill")]
        if skill_tools:
            return skill_tools
        return tools

    def _fallback_react_plan(self, state: PaperAgentState, step_count: int) -> dict:
        intent = state.get("intent", "paper_search")
        skill = state.get("selected_skill", "")
        slots = state.get("slots", {})

        # Try to use the intent-selected skill first
        if skill and skill in self.tool_registry:
            args: dict[str, Any] = {
                "user_message": state.get("user_message", ""),
                "topic": state.get("normalized_query") or state.get("query") or "machine learning",
                "top_n": state.get("top_n", 2),
                "candidate_k": state.get("candidate_k", 20),
                "session_id": state.get("session_id", ""),
            }
            if intent == "paper_deep_read":
                args["arxiv_id"] = slots.get("arxiv_id", "") or slots.get("paper_ref", "")
                args["paper_ref"] = slots.get("paper_ref", "")
            elif intent == "paper_compare":
                args["arxiv_ids"] = slots.get("arxiv_ids", [])
            elif intent == "memory_profile":
                args["action"] = slots.get("action", "read")
                args["key"] = slots.get("key", "")
                args["value"] = slots.get("value", "")
            return {
                "current_node": "react_plan",
                "step_count": step_count,
                "selected_tool": skill,
                "tool_arguments": args,
                "reasoning_summary": f"LLM 不可用，直接调用 {skill}。",
                "status": "running",
            }

        # Fallback for paper_search without skill registered
        if intent == "paper_search" and "paper_search_card_skill" in self.tool_registry:
            return {
                "current_node": "react_plan",
                "step_count": step_count,
                "selected_tool": "paper_search_card_skill",
                "tool_arguments": {
                    "user_message": state.get("user_message", ""),
                    "topic": state.get("normalized_query") or state.get("query") or "machine learning",
                    "top_n": state.get("top_n", 2),
                    "candidate_k": state.get("candidate_k", 20),
                },
                "reasoning_summary": "LLM 不可用，使用稳定论文搜索 Skill。",
                "status": "running",
            }

        return {
            "current_node": "react_plan",
            "step_count": step_count,
            "selected_tool": "final_answer",
            "tool_arguments": {},
            "reasoning_summary": "LLM 不可用，无法处理该意图。",
            "status": "success",
        }

    def _react_prompt(self, state: PaperAgentState) -> str:
        memory_lines = self._memory_summary(state)
        return (
            f"User request: {state.get('user_message', '')}\n"
            f"Intent: {state.get('intent', '')}\n"
            f"Query: {state.get('normalized_query') or state.get('query', '')}\n"
            f"Top N: {state.get('top_n', 2)}\n"
            f"Candidate K: {state.get('candidate_k', 20)}\n"
            f"Memory context:\n{memory_lines}\n"
            f"State summary:\n{self._state_summary(state)}"
        )

    def _state_summary(self, state: PaperAgentState) -> str:
        observations = state.get("observations", [])[-4:]
        if not observations:
            return "No observations yet."
        lines = []
        for index, obs in enumerate(observations, 1):
            status = "OK" if obs.get("success") else "FAIL"
            text = str(obs.get("message") or obs.get("error") or obs)[:160]
            lines.append(f"{index}. {status}: {text}")
        return "\n".join(lines)

    def _parse_tool_arguments(self, raw: Any) -> dict[str, Any]:
        if isinstance(raw, dict):
            return raw
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def _build_paper_cards(self, papers: list[dict], query: str) -> list[PaperCardItem]:
        cards = []
        for paper in papers:
            authors = paper.get("authors", [])
            if isinstance(authors, str):
                authors = [a.strip() for a in authors.split(",") if a.strip()]

            categories = paper.get("categories", [])
            if isinstance(categories, str):
                categories = [c.strip() for c in categories.split(",") if c.strip()]

            cards.append(PaperCardItem(
                arxiv_id=paper.get("arxiv_id", ""),
                title=paper.get("title", ""),
                authors=authors[:5],
                published_date=paper.get("published_date", ""),
                categories=categories[:3],
                arxiv_url=paper.get("arxiv_url", ""),
                pdf_url=paper.get("pdf_url", ""),
                summary=paper.get("summary", paper.get("abstract", "")),
                core_problem=paper.get("core_problem", "基于摘要无法确定核心问题"),
                method=paper.get("method", "详见论文"),
                result=paper.get("result", "详见论文"),
                summary_source=paper.get("summary_source", "metadata_only"),
                actions=["collect", "parse", "view_pdf"],
            ))
        return cards

    def _dedupe_papers(self, papers: list[dict]) -> list[dict]:
        seen = set()
        unique = []
        for paper in papers:
            arxiv_id = paper.get("arxiv_id", "")
            if arxiv_id and arxiv_id not in seen:
                seen.add(arxiv_id)
                unique.append(paper)
        return unique

    async def _persist_memory_after_run(
        self,
        session_id: str,
        user_message: str,
        trace_id: str,
        final_state: PaperAgentState,
        response: ChatResponse,
    ) -> None:
        try:
            papers = [paper.model_dump() for paper in response.papers]
            await self.short_memory.add_assistant_message(
                session_id=session_id,
                content=response.message,
                metadata={
                    "trace_id": trace_id,
                    "response_type": response.type,
                    "papers": papers,
                },
            )
            if response.success and papers:
                query = (
                    final_state.get("normalized_query")
                    or final_state.get("query")
                    or final_state.get("interest_query")
                    or ""
                )
                await self.semantic_memory.remember_search(
                    session_id=session_id,
                    trace_id=trace_id,
                    query=query,
                    user_message=user_message,
                    papers=papers,
                )
        except Exception as exc:
            logger.warning(f"Failed to persist memory for trace {trace_id}: {exc}")

    def _tool_group_id(self, state: PaperAgentState, step_count: int) -> str:
        return f"{state.get('trace_id', 'trace')}:{step_count}"

    def _is_interest_search(self, message: str) -> bool:
        text = message.lower()
        interest_terms = [
            "\u611f\u5174\u8da3",
            "\u6211\u7684\u5174\u8da3",
            "\u6211\u559c\u6b22",
            "\u6211\u5173\u6ce8",
            "interested",
            "my interests",
            "something i like",
        ]
        paper_terms = ["paper", "arxiv", "\u8bba\u6587", "\u6587\u732e"]
        return any(term in text for term in interest_terms) and any(term in text for term in paper_terms)

    def _looks_like_interest_placeholder(self, topic: str) -> bool:
        text = topic.lower()
        return any(term in text for term in [
            "interested",
            "my interests",
            "\u611f\u5174\u8da3",
            "\u6211\u7684\u5174\u8da3",
        ])

    def _refine_intent(self, message: str, intent_result: dict, state: PaperAgentState) -> dict:
        """Refine intent classification for new Phase 10 intents."""
        current = intent_result.get("intent", "")
        confidence = intent_result.get("confidence", 0.5)
        entities = intent_result.get("entities", {})

        if current in ("paper_parse",) and self._asks_for_deep_read(message):
            return {"intent": "paper_deep_read", "confidence": max(confidence, 0.85), "entities": entities}

        if self._asks_for_survey(message):
            return {"intent": "literature_survey", "confidence": max(confidence, 0.88), "entities": entities}

        if self._asks_for_compare(message):
            return {"intent": "paper_compare", "confidence": max(confidence, 0.88), "entities": entities}

        if self._is_memory_profile_request(message):
            return {"intent": "memory_profile", "confidence": max(confidence, 0.85), "entities": entities}

        if self._is_trace_diagnosis_request(message):
            return {"intent": "trace_diagnosis", "confidence": max(confidence, 0.90), "entities": entities}

        return intent_result

    def _asks_for_deep_read(self, message: str) -> bool:
        text = message.lower()
        return any(term in text for term in [
            "deep read", "deep-read", "deep_read",
            "\u6df1\u5ea6\u9605\u8bfb", "\u5168\u6587\u7cbe\u8bfb", "\u7cbe\u8bfb\u8fd9\u7bc7", "\u8be6\u7ec6\u5206\u6790\u8fd9\u7bc7",
            "generate report", "\u751f\u6210\u62a5\u544a", "\u6df1\u5ea6\u89e3\u6790",
            "generate.*report.*this", "parse.*this.*paper",
            "read.*this.*paper", "analyze.*this.*paper",
        ])

    def _asks_for_survey(self, message: str) -> bool:
        text = message.lower()
        return any(term in text for term in [
            "survey", "\u7efc\u8ff0", "literature review", "\u6982\u89c8",
            "\u6587\u732e\u7efc\u8ff0", "\u8c03\u7814", "overview", "\u603b\u7ed3.*\u9886\u57df",
            "write.*survey", "\u751f\u6210.*\u7efc\u8ff0", "make.*survey",
        ])

    def _asks_for_compare(self, message: str) -> bool:
        text = message.lower()
        return any(term in text for term in [
            "compare", "\u5bf9\u6bd4", "\u6bd4\u8f83", "\u533a\u522b", "\u5f02\u540c",
            "diff", "\u54ea\u4e2a\u66f4\u597d", "\u4f18\u7f3a\u70b9", "\u5bf9\u6bd4\u5206\u6790",
        ])

    def _is_memory_profile_request(self, message: str) -> bool:
        text = message.lower()
        return any(term in text for term in [
            "\u504f\u597d", "prefer", "\u8bbe\u7f6e\u504f\u597d", "\u66f4\u65b0\u504f\u597d",
            "recommend more", "fewer", "\u5c11\u63a8\u8350", "\u591a\u63a8\u8350",
            "in the future.*recommend", "\u4ee5\u540e.*\u63a8\u8350",
            "\u4e0d\u611f\u5174\u8da3.*\u4e3b\u9898", "\u66f4\u5173\u6ce8", "remember.*prefer",
        ]) and not self._is_paper_search_request(message)

    def _is_trace_diagnosis_request(self, message: str) -> bool:
        text = message.lower()
        return any(term in text for term in [
            "diagnos", "\u8bca\u65ad", "\u4e3a\u4ec0\u4e48\u5931\u8d25", "\u5931\u8d25\u539f\u56e0",
            "\u51fa\u9519", "what went wrong", "debug",
            "last.*task.*fail", "\u6700\u8fd1.*\u4efb\u52a1.*\u5931\u8d25",
            "\u4e3a\u4ec0\u4e48.*\u6700\u540e.*\u4efb\u52a1", "trace.*fail",
            "last.*job.*fail", "\u4e0a\u6b21.*\u4efb\u52a1.*\u5931\u8d25",
        ])

    def _is_paper_search_request(self, message: str) -> bool:
        text = message.lower()
        search_terms = ["find", "search", "recommend", "\u627e", "\u641c", "\u63a8\u8350"]
        paper_terms = ["paper", "arxiv", "\u8bba\u6587", "\u6587\u732e"]
        return any(term in text for term in search_terms) and any(term in text for term in paper_terms)

    def _extract_topic_from_message(self, message: str) -> str:
        patterns = [
            r"(?:about|on|regarding)\s+(.+?)(?:\s+paper|\s+papers|$)",
            r"\u5173\u4e8e\s*(.+?)\s*(?:\u7684)?\s*(?:\u8bba\u6587|\u6587\u732e|paper|papers)",
            r"(?:find|search|recommend)\s+(?:me\s+)?(?:\d+\s+)?(?:papers?\s+)?(?:about|on)?\s*(.+?)\s*(?:papers?|$)",
            r"(?:\u627e|\u641c|\u63a8\u8350).*?\s+([A-Za-z0-9_\-\s]+?)\s*(?:\u7684)?\s*(?:\u8bba\u6587|\u6587\u732e|paper|papers)",
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                topic = match.group(1).strip(" ,.;:，。")
                topic = re.sub(r"^\d+\s*", "", topic).strip()
                if topic:
                    return topic
        return ""

    def _select_referenced_paper(self, message: str, papers: list[dict[str, Any]]) -> dict[str, Any]:
        if not papers:
            return {}
        index = self._referenced_index(message)
        if index is None:
            text = message.lower()
            if any(term in text for term in ["\u4e0a\u9762", "\u521a\u624d", "\u8fd9\u7bc7", "previous", "that paper"]):
                index = 0
        if index is None or index < 0 or index >= len(papers):
            return {}
        return papers[index]

    def _referenced_index(self, message: str) -> int | None:
        text = message.lower()
        digit_match = re.search(r"(?:\u7b2c)?\s*(\d+)\s*(?:\u7bc7|\u4e2a|paper|one|th|st|nd|rd)", text)
        if digit_match:
            return max(0, int(digit_match.group(1)) - 1)

        number_words = {
            "\u4e00": 1,
            "\u4e8c": 2,
            "\u4e24": 2,
            "\u4e09": 3,
            "\u56db": 4,
            "\u4e94": 5,
            "first": 1,
            "second": 2,
            "third": 3,
            "fourth": 4,
            "fifth": 5,
        }
        for word, number in number_words.items():
            if word in text:
                if word.isascii() or f"\u7b2c{word}" in text or f"{word}\u7bc7" in text or f"{word}\u4e2a" in text:
                    return number - 1
        return None

    def _asks_for_similar_papers(self, message: str) -> bool:
        text = message.lower()
        return any(term in text for term in [
            "similar",
            "related",
            "more like",
            "\u7c7b\u4f3c",
            "\u76f8\u4f3c",
            "\u76f8\u5173",
            "\u518d\u627e",
            "\u66f4\u591a",
        ])

    def _paper_memory_query(self, paper: dict[str, Any]) -> str:
        categories = paper.get("categories", [])
        if isinstance(categories, list):
            categories_text = " ".join(categories[:3])
        else:
            categories_text = str(categories)
        return " ".join(part for part in [
            paper.get("title", ""),
            categories_text,
            paper.get("summary", ""),
        ] if part).strip()

    def _memory_summary(self, state: PaperAgentState) -> str:
        lines = []
        conversation = state.get("conversation_summary", "")
        if conversation:
            lines.append("Recent conversation:")
            lines.append(conversation[-1500:])

        prefs = state.get("user_preferences", {})
        topics = prefs.get("preferred_topics") or []
        categories = prefs.get("preferred_categories") or []
        if topics or categories:
            lines.append(f"Long-term user interests: topics={topics[:6]}, categories={categories[:6]}")

        last_papers = state.get("last_papers", [])
        if last_papers:
            paper_lines = []
            for index, paper in enumerate(last_papers[:5], 1):
                paper_lines.append(f"{index}. {paper.get('title', '')} ({paper.get('arxiv_id', '')})")
            lines.append("Last paper results:\n" + "\n".join(paper_lines))

        memories = state.get("long_term_memories", [])
        if memories:
            memory_lines = []
            for memory in memories[:5]:
                memory_lines.append(
                    f"- [{memory.get('source_type', '')}] {memory.get('title', '')} score={memory.get('score', 0)}"
                )
            lines.append("Retrieved long-term memories:\n" + "\n".join(memory_lines))

        return "\n".join(lines) if lines else "No memory context."

    def _to_chat_response(self, response: dict, trace_id: str) -> ChatResponse:
        papers = response.get("papers", [])
        if papers and isinstance(papers[0], PaperCardItem):
            paper_items = papers
        else:
            paper_items = [PaperCardItem(**paper) for paper in papers]
        return ChatResponse(
            success=response.get("success", True),
            type=response.get("type", "paper_search_result"),
            trace_id=response.get("trace_id", trace_id),
            message=response.get("message", ""),
            papers=paper_items,
            error_code=response.get("error_code"),
            detail=response.get("detail"),
        )
