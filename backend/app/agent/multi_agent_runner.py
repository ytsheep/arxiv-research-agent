"""MultiAgentGraphRunner: LangGraph workflow for compound research tasks.

Runs Supervisor -> Executor -> Reviewer cycles with checkpointed state.
Does NOT replace LangGraphAgentRunner; used only for detected compound tasks.
"""

from __future__ import annotations

import os
import re
from typing import Any

import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, StateGraph

from app.agent.workflow_state import WorkflowState
from app.agent.message_schema import AgentMessage
from app.agent.message_bus import MessageBus

from app.agent.supervisor.planner import SupervisorPlanner
from app.agent.supervisor.dispatcher import SupervisorDispatcher
from app.agent.executor.executor_agent import ExecutorAgent
from app.agent.reviewer.reviewer_agent import ReviewerAgent
from app.agent.reviewer.final_composer import FinalComposer
from app.agent.tool_registry import ToolRegistry

from app.core.config import settings
from app.core.logging import logger
from app.schemas.chat import ChatResponse, PaperCardItem
from app.services.memory_service import SemanticMemoryService, ShortTermMemoryService
from app.tools.trace_tool import TraceTool

MAX_RETRIES = 2
MAX_REPLANS = 2


class MultiAgentGraphRunner:
    """Runs compound tasks through Supervisor -> Executor -> Reviewer loops."""

    def __init__(
        self,
        trace_tool: TraceTool,
        tool_registry: ToolRegistry,
    ):
        self.trace_tool = trace_tool
        self.tool_registry = tool_registry

        self.planner = SupervisorPlanner()
        self.dispatcher = SupervisorDispatcher()
        self.executor = ExecutorAgent(tool_registry)
        self.reviewer = ReviewerAgent()
        self.composer = FinalComposer()

        self.short_memory = ShortTermMemoryService()
        self.semantic_memory = SemanticMemoryService()

        self._graph = None
        self._checkpointer: AsyncSqliteSaver | None = None
        self._checkpoint_conn: aiosqlite.Connection | None = None

    # ── Public API ─────────────────────────────────────────────────

    async def run_chat(self, message: str, session_id: str) -> ChatResponse:
        await self.short_memory.add_user_message(session_id, message)
        messages = await self.short_memory.load_messages(session_id)
        last_papers = await self.short_memory.get_last_papers(session_id)
        user_preferences = await self.semantic_memory.load_user_preferences()
        long_term_memories = await self.semantic_memory.retrieve(
            query=message, session_id=session_id, top_k=5,
        )

        trace = self.trace_tool.create(
            task_type="multi_agent_workflow",
            user_input=message,
            tags=["multi_agent", "compound"],
        )

        graph = await self._get_graph()
        config = {"configurable": {"thread_id": trace.trace_id}}

        initial_state: WorkflowState = {
            "trace_id": trace.trace_id,
            "session_id": session_id,
            "workflow_id": trace.trace_id,
            "user_message": message,
            "complexity": "compound",
            "status": "running",
            "error": "",
            "task_plan": [],
            "task_outputs": {},
            "pending_tasks": [],
            "running_tasks": [],
            "completed_tasks": [],
            "failed_tasks": [],
            "message_history": [],
            "last_review_decision": "",
            "retry_count": 0,
            "replan_count": 0,
            "max_retries": MAX_RETRIES,
            "max_replans": MAX_REPLANS,
            "user_preferences": user_preferences,
            "long_term_memories": long_term_memories,
            "last_papers": last_papers,
            "current_node": "",
            "top_n": 2,
            "candidate_k": 20,
            "messages": messages,
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
            await self._persist_memory(session_id, message, trace.trace_id, chat_response)
            self._cache_workflow_state(trace.trace_id, final_state)
            return chat_response
        except Exception as exc:
            logger.error(f"MultiAgent workflow failed: {exc}")
            await self.trace_tool.complete(
                trace.trace_id, status="failed", error_message=str(exc), trace=trace,
            )
            await self.short_memory.add_assistant_message(
                session_id, f"Task failed: {exc}",
                metadata={"trace_id": trace.trace_id, "response_type": "error"},
            )
            return ChatResponse(
                success=False, type="error", trace_id=trace.trace_id,
                message=f"复合任务执行失败: {exc}", papers=[],
            )

    async def close(self) -> None:
        if self._checkpoint_conn:
            await self._checkpoint_conn.close()
            self._checkpoint_conn = None
            self._checkpointer = None
            self._graph = None

    # ── Graph construction ─────────────────────────────────────────

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
            name="multi_agent_graph",
        )
        return self._graph

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(WorkflowState)

        graph.add_node("supervisor_init", self._supervisor_init_node)
        graph.add_node("supervisor_plan", self._supervisor_plan_node)
        graph.add_node("supervisor_dispatch", self._supervisor_dispatch_node)
        graph.add_node("executor_run", self._executor_run_node)
        graph.add_node("reviewer_check", self._reviewer_check_node)
        graph.add_node("workflow_review", self._workflow_review_node)
        graph.add_node("composer_build", self._composer_build_node)
        graph.add_node("error_handler", self._error_handler_node)

        graph.add_edge(START, "supervisor_init")
        graph.add_edge("supervisor_init", "supervisor_plan")
        graph.add_conditional_edges("supervisor_plan", self._route_after_plan, {
            "dispatch": "supervisor_dispatch",
            "error": "error_handler",
        })
        graph.add_conditional_edges("supervisor_dispatch", self._route_after_dispatch, {
            "executor": "executor_run",
            "workflow_review": "workflow_review",
            "error": "error_handler",
        })
        graph.add_edge("executor_run", "reviewer_check")
        graph.add_conditional_edges("reviewer_check", self._route_after_reviewer, {
            "dispatch": "supervisor_dispatch",
            "plan": "supervisor_plan",
            "workflow_review": "workflow_review",
            "error": "error_handler",
        })
        graph.add_conditional_edges("workflow_review", self._route_after_workflow_review, {
            "dispatch": "supervisor_dispatch",
            "composer": "composer_build",
            "error": "error_handler",
        })
        graph.add_edge("composer_build", END)
        graph.add_edge("error_handler", END)

        return graph

    # ── Nodes ──────────────────────────────────────────────────────

    async def _supervisor_init_node(self, state: WorkflowState) -> dict:
        logger.info(f"[MultiAgent] Init workflow={state.get('workflow_id', '')}")
        return {"current_node": "supervisor_init", "status": "running"}

    async def _supervisor_plan_node(self, state: WorkflowState) -> dict:
        user_message = state.get("user_message", "")
        prefs = state.get("user_preferences", {})
        long_term = state.get("long_term_memories", [])

        plan_result = await self.planner.plan(user_message, prefs, long_term)

        if plan_result.get("success") and plan_result.get("task_plan"):
            task_plan = plan_result["task_plan"]
            pending = [t.get("task_id", "") for t in task_plan]
            msg = AgentMessage(
                workflow_id=state.get("workflow_id", ""),
                sender="supervisor",
                receiver="executor",
                message_type="task.planned",
                payload={"task_plan": task_plan, "reason": plan_result.get("reason", "")},
            )
            updated_history = MessageBus.publish(state, msg)
            logger.info(f"[MultiAgent] Plan: {len(task_plan)} tasks, pending={pending}")

            self._cache_workflow_state(state.get("workflow_id", ""), state)

            return {
                "current_node": "supervisor_plan",
                "task_plan": task_plan,
                "task_plan_raw": plan_result.get("raw_llm_output", {}),
                "pending_tasks": pending,
                "completed_tasks": list(state.get("completed_tasks", [])),
                "failed_tasks": list(state.get("failed_tasks", [])),
                "task_outputs": state.get("task_outputs", {}),
                "message_history": updated_history,
                "retry_count": 0,
                "status": "running",
            }

        # Empty plan — fallback to simple text response
        logger.warning(f"[MultiAgent] Empty plan, falling back")
        return {
            "current_node": "supervisor_plan",
            "status": "fallback",
            "error": plan_result.get("reason", "Could not build task plan"),
            "final_response": {
                "success": True,
                "type": "chat_result",
                "trace_id": state.get("trace_id", ""),
                "message": "无法将您的请求分解为多个子任务，请尝试更具体的描述。",
                "papers": [],
            },
        }

    async def _supervisor_dispatch_node(self, state: WorkflowState) -> dict:
        task_plan = state.get("task_plan", [])
        completed = state.get("completed_tasks", [])
        running = state.get("running_tasks", [])
        failed = state.get("failed_tasks", [])

        # Check for blocked/deadlock
        if self.dispatcher.has_blocked_tasks(task_plan, completed, running, failed):
            return {
                "current_node": "supervisor_dispatch",
                "status": "error",
                "error": "Circular dependency detected: tasks blocked with no ready candidates",
                "last_review_decision": "replan",
            }

        ready = self.dispatcher.find_ready_tasks(task_plan, completed, running, failed)
        if not ready:
            return {"current_node": "supervisor_dispatch", "status": "idle"}

        next_task_id = ready[0]
        task_item = self.dispatcher.find_task_item(task_plan, next_task_id) or {}

        msg = AgentMessage(
            workflow_id=state.get("workflow_id", ""),
            task_id=next_task_id,
            sender="supervisor",
            receiver="executor",
            message_type="task.assigned",
            payload={"task_id": next_task_id, "task_type": task_item.get("task_type", ""),
                     "description": task_item.get("description", "")},
        )
        updated_history = MessageBus.publish(state, msg)

        logger.info(f"[MultiAgent] Dispatch {next_task_id} ({task_item.get('task_type', '')})")

        return {
            "current_node": "supervisor_dispatch",
            "current_task_id": next_task_id,
            "running_tasks": list(running) + [next_task_id],
            "pending_tasks": [t for t in state.get("pending_tasks", []) if t != next_task_id],
            "message_history": updated_history,
        }

    async def _executor_run_node(self, state: WorkflowState) -> dict:
        task_id = state.get("current_task_id", "")
        task_plan = state.get("task_plan", [])
        task_item = self.dispatcher.find_task_item(task_plan, task_id) or {}

        result = await self.executor.execute(
            task_item=task_item,
            task_outputs=state.get("task_outputs", {}),
            user_message=state.get("user_message", ""),
            user_preferences=state.get("user_preferences", {}),
            default_top_n=state.get("top_n", 2),
            default_candidate_k=state.get("candidate_k", 20),
        )

        task_outputs = dict(state.get("task_outputs", {}))
        task_outputs[task_id] = result

        msg = AgentMessage(
            workflow_id=state.get("workflow_id", ""),
            task_id=task_id,
            sender="executor",
            receiver="reviewer",
            message_type="task.result",
            payload={
                "task_id": task_id,
                "success": result.get("success", False),
                "output_keys": list(result.keys()),
            },
        )
        updated_history = MessageBus.publish(state, msg)

        logger.info(f"[MultiAgent] Executed {task_id}: success={result.get('success')}")

        # Move task from running to completed or failed based on preliminary check
        running = [t for t in state.get("running_tasks", []) if t != task_id]
        if result.get("success"):
            completed = list(state.get("completed_tasks", [])) + [task_id]
            failed = list(state.get("failed_tasks", []))
        else:
            completed = list(state.get("completed_tasks", []))
            failed = list(state.get("failed_tasks", [])) + [task_id]

        return {
            "current_node": "executor_run",
            "task_outputs": task_outputs,
            "running_tasks": running,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "message_history": updated_history,
        }

    async def _reviewer_check_node(self, state: WorkflowState) -> dict:
        task_id = state.get("current_task_id", "")
        task_outputs = state.get("task_outputs", {})
        task_output = task_outputs.get(task_id, {})
        task_plan = state.get("task_plan", [])
        task_item = self.dispatcher.find_task_item(task_plan, task_id) or {}

        review = await self.reviewer.review_task(
            task_type=task_item.get("task_type", ""),
            task_output=task_output,
            task_item=task_item,
            retry_count=task_item.get("retry_count", 0),
            max_retries=state.get("max_retries", MAX_RETRIES),
        )

        decision = review.get("decision", "continue")
        logger.info(f"[MultiAgent] Review {task_id}: decision={decision}")

        msg = AgentMessage(
            workflow_id=state.get("workflow_id", ""),
            task_id=task_id,
            sender="reviewer",
            receiver="supervisor",
            message_type="task.reviewed",
            payload={"task_id": task_id, "decision": decision, "reason": review.get("reason", "")},
        )
        updated_history = MessageBus.publish(state, msg)

        # Handle retry: move task back to pending/running
        retry_count = state.get("retry_count", 0)
        completed = list(state.get("completed_tasks", []))
        failed = list(state.get("failed_tasks", []))
        pending = list(state.get("pending_tasks", []))
        running = list(state.get("running_tasks", []))

        if decision == "retry":
            retry_count += 1
            # Move from completed/failed back to pending for retry
            if task_id in completed:
                completed.remove(task_id)
            if task_id in failed:
                failed.remove(task_id)
            pending.append(task_id)
            task_item["retry_count"] = task_item.get("retry_count", 0) + 1
        elif decision == "replan":
            retry_count = 0
            state_replan_count = state.get("replan_count", 0) + 1
            return {
                "current_node": "reviewer_check",
                "last_review_decision": decision,
                "message_history": updated_history,
                "retry_count": retry_count,
                "replan_count": state_replan_count,
                "completed_tasks": [t for t in completed if t != task_id],
                "failed_tasks": list(set(failed) | {task_id}),
            }

        return {
            "current_node": "reviewer_check",
            "last_review_decision": decision,
            "message_history": updated_history,
            "retry_count": retry_count,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "pending_tasks": pending,
        }

    async def _workflow_review_node(self, state: WorkflowState) -> dict:
        task_plan = state.get("task_plan", [])
        completed = state.get("completed_tasks", [])
        failed = state.get("failed_tasks", [])

        review = await self.reviewer.review_workflow(task_plan, completed, failed)
        decision = review.get("decision", "finish")
        logger.info(f"[MultiAgent] Workflow review: {decision}")

        return {
            "current_node": "workflow_review",
            "last_review_decision": decision,
            "status": decision if decision in ("finish", "partial_final") else "running",
        }

    async def _composer_build_node(self, state: WorkflowState) -> dict:
        task_outputs = state.get("task_outputs", {})
        user_message = state.get("user_message", "")
        trace_id = state.get("trace_id", "")
        task_plan = state.get("task_plan", [])
        completed = state.get("completed_tasks", [])
        failed = state.get("failed_tasks", [])

        task_summary = []
        for item in task_plan:
            tid = item.get("task_id", "")
            if tid in completed:
                status = "completed"
            elif tid in failed:
                status = "failed"
            else:
                status = "skipped"
            task_summary.append({
                "task_id": tid,
                "task_type": item.get("task_type", ""),
                "status": status,
                "summary": item.get("description", ""),
            })

        final = await self.composer.compose(
            task_outputs=task_outputs,
            user_message=user_message,
            trace_id=trace_id,
            state_summary={"task_summary": task_summary},
        )

        msg = AgentMessage(
            workflow_id=state.get("workflow_id", ""),
            sender="reviewer",
            receiver="supervisor",
            message_type="workflow.final",
            payload=final,
        )
        updated_history = MessageBus.publish(state, msg)

        self._cache_workflow_state(state.get("workflow_id", ""), state)

        return {
            "current_node": "composer_build",
            "final_response": final,
            "status": "success",
            "message_history": updated_history,
        }

    async def _error_handler_node(self, state: WorkflowState) -> dict:
        error = state.get("error", "Unknown error in multi-agent workflow")
        logger.error(f"[MultiAgent] Error: {error}")

        msg = AgentMessage(
            workflow_id=state.get("workflow_id", ""),
            sender="supervisor",
            receiver="supervisor",
            message_type="workflow.error",
            payload={"error": error},
        )
        updated_history = MessageBus.publish(state, msg)

        completed = state.get("completed_tasks", [])
        task_outputs = state.get("task_outputs", {})
        papers = []
        for output in task_outputs.values():
            p = output.get("papers", [])
            if p:
                papers.extend(p)

        return {
            "current_node": "error_handler",
            "status": "failed",
            "error": error,
            "message_history": updated_history,
            "final_response": {
                "success": False,
                "type": "error",
                "trace_id": state.get("trace_id", ""),
                "message": f"任务执行中发生错误: {error}\n\n已完成 {len(completed)} 个子任务。",
                "papers": papers[:5],
            },
        }

    # ── Routing ────────────────────────────────────────────────────

    @staticmethod
    def _route_after_plan(state: WorkflowState) -> str:
        if state.get("status") == "fallback":
            return "error"
        task_plan = state.get("task_plan", [])
        if not task_plan:
            return "error"
        return "dispatch"

    @staticmethod
    def _route_after_dispatch(state: WorkflowState) -> str:
        if state.get("status") == "error":
            return "error"
        if state.get("current_task_id"):
            return "executor"
        return "workflow_review"

    @staticmethod
    def _route_after_reviewer(state: WorkflowState) -> str:
        decision = state.get("last_review_decision", "continue")
        replan_count = state.get("replan_count", 0)
        max_replans = state.get("max_replans", MAX_REPLANS)

        if decision == "replan" and replan_count >= max_replans:
            return "workflow_review"
        if decision in ("retry", "replan"):
            return "plan"
        if decision == "continue":
            return "dispatch"
        if decision in ("partial_final", "finish"):
            return "workflow_review"
        return "error"

    @staticmethod
    def _route_after_workflow_review(state: WorkflowState) -> str:
        decision = state.get("last_review_decision", "finish")
        if decision in ("finish", "partial_final"):
            return "composer"
        if decision == "continue":
            return "dispatch"
        return "error"

    # ── Response & Memory ──────────────────────────────────────────

    def _to_chat_response(self, final_response: dict, trace_id: str) -> ChatResponse:
        papers_raw = final_response.get("papers", [])
        papers = []
        for p in papers_raw:
            try:
                papers.append(PaperCardItem(
                    arxiv_id=p.get("arxiv_id", p.get("arxivId", "")),
                    title=p.get("title", ""),
                    authors=p.get("authors", []),
                    published_date=p.get("published_date", p.get("publishedDate", "")),
                    categories=p.get("categories", []),
                    arxiv_url=p.get("arxiv_url", p.get("arxivUrl", "")),
                    pdf_url=p.get("pdf_url", p.get("pdfUrl", "")),
                    summary=p.get("summary", ""),
                    core_problem=p.get("core_problem", p.get("coreProblem", "")),
                    method=p.get("method", ""),
                    result=p.get("result", ""),
                    summary_source=p.get("summary_source", p.get("summarySource", "metadata_only")),
                ))
            except Exception:
                pass

        return ChatResponse(
            success=final_response.get("success", True),
            type=final_response.get("type", "workflow_result"),
            trace_id=trace_id,
            message=final_response.get("message", ""),
            papers=papers,
            metadata=final_response.get("metadata", {}),
        )

    async def _persist_memory(self, session_id: str, user_message: str, trace_id: str, response: ChatResponse):
        try:
            metadata = {
                "trace_id": trace_id,
                "response_type": response.type,
                "papers": [p.model_dump() for p in response.papers],
            }
            if response.metadata:
                metadata["workflow_metadata"] = response.metadata
            await self.short_memory.add_assistant_message(
                session_id, response.message,
                metadata=metadata,
            )
            if response.papers:
                await self.semantic_memory.remember_search(
                    session_id=session_id,
                    query=user_message,
                    papers=[p.model_dump() for p in response.papers],
                )
        except Exception as e:
            logger.warning(f"Memory persist failed: {e}")

    def _cache_workflow_state(self, workflow_id: str, state: dict):
        """Fire-and-forget cache of lightweight workflow projection."""
        if not workflow_id:
            return
        try:
            from app.services.cache_service import cache_service
            import asyncio
            projection = {
                "workflow_id": workflow_id,
                "trace_id": state.get("trace_id", ""),
                "status": state.get("status", "running"),
                "current_task_id": state.get("current_task_id", ""),
                "completed_tasks": list(state.get("completed_tasks", [])),
                "failed_tasks": list(state.get("failed_tasks", [])),
                "last_review_decision": state.get("last_review_decision", ""),
                "updated_at": "",
            }
            asyncio.ensure_future(cache_service.cache_workflow_state(workflow_id, projection))
        except Exception:
            pass
