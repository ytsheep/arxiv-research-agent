"""Paper Search Card Skill: fixed pipeline for searching arXiv and generating cards.

Wraps: intent classify → query normalize → arxiv search → rerank → card summary.
This is a safe, pre-defined workflow that the ReAct Agent can call as a single tool.
"""

from app.agent.intent_classifier import classify_intent, normalize_query
from app.tools.arxiv_tool import ArxivTool
from app.tools.rerank_tool import RerankTool
from app.tools.report_tool import ReportTool
from app.tools.trace_tool import TraceTool
from app.core.logging import logger


PAPER_SEARCH_CARD_SKILL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "paper_search_card_skill",
        "description": "Search arXiv papers and generate Chinese paper cards. This is a safe, pre-defined workflow that searches, reranks, and generates summaries. Use this when the user wants to find papers on a topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_message": {
                    "type": "string",
                    "description": "The original user message for intent classification",
                },
                "topic": {
                    "type": "string",
                    "description": "The research topic to search for",
                },
                "top_n": {
                    "type": "integer",
                    "description": "Number of top papers to return (default 2)",
                    "default": 2,
                },
                "candidate_k": {
                    "type": "integer",
                    "description": "Number of candidate papers to fetch from arXiv (default 20, max 50)",
                    "default": 20,
                },
            },
            "required": ["user_message", "topic"],
        },
    },
}


async def paper_search_card_skill(
    user_message: str = "",
    topic: str = "",
    top_n: int = 2,
    candidate_k: int = 20,
) -> dict:
    """Execute the paper search → card generation workflow."""
    trace_tool = TraceTool()
    arxiv_tool = ArxivTool()
    rerank_tool = RerankTool()
    report_tool = ReportTool()

    trace = trace_tool.create(task_type="paper_search", user_input=user_message or topic)
    logger.info(f"[Skill:paper_search_card trace={trace.trace_id}] topic={topic} top_n={top_n}")

    # Step 1: Intent / normalize
    intent_result = classify_intent(user_message or topic)
    raw_topic = topic or intent_result.get("entities", {}).get("topic", "")
    normalized_topic = normalize_query(raw_topic) if raw_topic else "machine learning"
    actual_top_n = intent_result.get("entities", {}).get("top_n", top_n)

    await trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="query_normalization",
        input_summary=f"raw_topic={raw_topic}, top_n={actual_top_n}",
        output_summary=f"normalized_topic={normalized_topic}, candidate_k={candidate_k}",
    )

    # Step 2: arXiv search
    search_result = await arxiv_tool.search(
        query=normalized_topic,
        max_results=min(candidate_k, 50),
    )
    await trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="arxiv_search",
        input_summary=f"query={normalized_topic}, max_results={candidate_k}",
        output_summary=f"found={len(search_result.get('papers', []))} papers",
    )

    papers = search_result.get("papers", [])
    if not papers:
        await trace_tool.complete(trace.trace_id, status="success", trace=trace)
        return {
            "success": True,
            "trace_id": trace.trace_id,
            "message": f'未找到与 "{normalized_topic}" 相关的论文。',
            "papers": [],
        }

    # Step 3: Rerank
    ranked = await rerank_tool.rerank(
        query=normalized_topic,
        papers=papers,
        top_n=actual_top_n,
    )
    await trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="candidate_rerank",
        input_summary=f"candidates={len(papers)}, top_n={actual_top_n}",
        output_summary=f"selected={len(ranked.get('ranked_papers', []))} papers",
    )

    ranked_papers = ranked.get("ranked_papers", papers[:actual_top_n])

    # Step 4: Generate LLM card summaries
    for paper in ranked_papers:
        try:
            summary_result = await report_tool.generate_card_summary(
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

    await trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="card_summary_generation",
        input_summary=f"papers_to_summarize={len(ranked_papers)}",
        output_summary=f"generated={len(ranked_papers)} cards",
    )

    await trace_tool.complete(trace.trace_id, status="success", trace=trace)

    return {
        "success": True,
        "trace_id": trace.trace_id,
        "message": f"找到 {len(ranked_papers)} 篇关于 {normalized_topic} 的论文",
        "papers": ranked_papers,
    }
