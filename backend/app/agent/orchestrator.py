"""Agent Orchestrator: coordinates intent recognition → tool execution → response."""

from app.agent.intent_classifier import classify_intent, normalize_query
from app.tools.trace_tool import TraceTool
from app.tools.arxiv_tool import ArxivTool
from app.tools.rerank_tool import RerankTool
from app.tools.report_tool import ReportTool
from app.schemas.chat import ChatResponse, PaperCardItem
from app.core.logging import logger


class AgentOrchestrator:
    def __init__(self):
        self.trace_tool = TraceTool()
        self.arxiv_tool = ArxivTool()
        self.rerank_tool = RerankTool()
        self.report_tool = ReportTool()

    async def handle_chat(self, message: str, session_id: str) -> ChatResponse:
        trace = self.trace_tool.create(task_type="chat", user_input=message)
        logger.info(f"[trace={trace.trace_id}] Processing chat: {message[:80]}")

        # Step 1: Intent recognition
        intent_result = classify_intent(message)
        await self.trace_tool.log_step(
            trace_id=trace.trace_id,
            step_name="intent_recognition",
            input_summary=f"user_input: {message[:100]}",
            output_summary=f"intent={intent_result['intent']}, confidence={intent_result['confidence']}",
        )

        # Step 2: Route based on intent
        if intent_result["intent"] == "paper_search":
            result = await self._paper_search_flow(intent_result, trace)
            await self.trace_tool.complete(trace.trace_id, status="success", trace=trace)
            return result

        elif intent_result["intent"] == "general_chat":
            await self.trace_tool.complete(trace.trace_id, status="success", trace=trace)
            return ChatResponse(
                success=True,
                type="general_chat",
                trace_id=trace.trace_id,
                message=(
                    '你好！我是 arXiv 论文助手。你可以输入研究方向搜索论文，例如：\n\n'
                    '"给我找 2 篇关于 agent 的论文"\n'
                    '"帮我推荐 3 篇最新的 RAG 方向论文"'
                ),
                papers=[],
            )

        else:
            await self.trace_tool.complete(trace.trace_id, status="success", trace=trace)
            return ChatResponse(
                success=True,
                type="unsupported",
                trace_id=trace.trace_id,
                message=f"意图识别为 {intent_result['intent']}，该功能将在后续版本支持。\n\n当前支持的意图：论文搜索 (paper_search)",
                papers=[],
            )

    async def _paper_search_flow(self, intent_result: dict, trace) -> ChatResponse:
        entities = intent_result.get("entities", {})

        # Step 2: Query normalization
        raw_topic = entities.get("topic", "")
        normalized_topic = normalize_query(raw_topic) if raw_topic else "machine learning"
        top_n = entities.get("top_n", 2)
        candidate_k = entities.get("candidate_k", 20)

        await self.trace_tool.log_step(
            trace_id=trace.trace_id,
            step_name="query_normalization",
            input_summary=f"raw_topic={raw_topic}, top_n={top_n}",
            output_summary=f"normalized_topic={normalized_topic}, candidate_k={candidate_k}",
        )

        # Step 3: arXiv search
        search_result = await self.arxiv_tool.search(
            query=normalized_topic,
            max_results=candidate_k,
        )
        await self.trace_tool.log_step(
            trace_id=trace.trace_id,
            step_name="arxiv_search",
            input_summary=f"query={normalized_topic}, max_results={candidate_k}",
            output_summary=f"found={len(search_result.get('papers', []))} papers",
        )

        papers = search_result.get("papers", [])
        if not papers:
            await self.trace_tool.log_step(
                trace_id=trace.trace_id,
                step_name="card_summary_generation",
                status="skipped",
                input_summary="no papers found",
            )
            return ChatResponse(
                success=True,
                type="paper_search_result",
                trace_id=trace.trace_id,
                message=f'未找到与 "{normalized_topic}" 相关的论文，请尝试其他关键词。',
                papers=[],
            )

        # Step 4: Rerank candidates → Top N
        ranked = await self.rerank_tool.rerank(
            query=normalized_topic,
            papers=papers,
            top_n=top_n,
        )
        await self.trace_tool.log_step(
            trace_id=trace.trace_id,
            step_name="candidate_rerank",
            input_summary=f"candidates={len(papers)}, top_n={top_n}",
            output_summary=f"selected={len(ranked.get('ranked_papers', []))} papers",
        )

        # Step 5: Generate paper cards with LLM-enhanced summary
        ranked_papers = ranked.get("ranked_papers", papers[:top_n])

        # Generate LLM-enhanced summaries for each paper
        for paper in ranked_papers:
            try:
                summary_result = await self.report_tool.generate_card_summary(
                    paper=paper,
                    query=normalized_topic,
                )
                if summary_result.get("success") and summary_result.get("summary"):
                    s = summary_result["summary"]
                    paper["summary"] = s.get("summary", paper.get("abstract", ""))
                    paper["core_problem"] = s.get("core_problem", "")
                    paper["method"] = s.get("method", "")
                    paper["result"] = s.get("result", "")
                    paper["summary_source"] = s.get("summary_source", "metadata_only")
            except Exception as e:
                logger.warning(f"LLM summary failed for {paper.get('arxiv_id')}: {e}")

        card_items = self._build_paper_cards(ranked_papers, normalized_topic)

        await self.trace_tool.log_step(
            trace_id=trace.trace_id,
            step_name="card_summary_generation",
            input_summary=f"papers_to_summarize={len(card_items)}",
            output_summary=f"generated={len(card_items)} cards",
        )

        return ChatResponse(
            success=True,
            type="paper_search_result",
            trace_id=trace.trace_id,
            message=f"找到 {len(card_items)} 篇关于 {normalized_topic} 的论文",
            papers=card_items,
        )

    def _build_paper_cards(self, papers: list[dict], query: str) -> list[PaperCardItem]:
        """Build paper card items from ranked papers."""
        cards = []
        for paper in papers:
            authors = paper.get("authors", [])
            if isinstance(authors, str):
                authors = [a.strip() for a in authors.split(",") if a.strip()]

            categories = paper.get("categories", [])
            if isinstance(categories, str):
                categories = [c.strip() for c in categories.split(",") if c.strip()]

            card = PaperCardItem(
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
            )
            cards.append(card)
        return cards
