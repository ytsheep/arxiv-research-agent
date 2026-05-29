"""Paper Select Best Skill: select the best paper from candidates.

Uses LLM-based selection with comparison context when available,
falls back to deterministic scoring when LLM is unavailable.
"""

from app.tools.llm_client import llm_client
from app.tools.trace_tool import TraceTool
from app.services.memory_service import SemanticMemoryService
from app.core.logging import logger

PAPER_SELECT_BEST_SKILL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "paper_select_best_skill",
        "description": "Select the best paper from multiple candidates based on scores, comparison results, user preferences, and task goal. Use when the user wants to pick the best paper among several.",
        "parameters": {
            "type": "object",
            "properties": {
                "papers": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of candidate papers with scores and summaries",
                },
                "comparison": {
                    "type": "object",
                    "description": "Optional comparison result from paper_compare_skill for richer selection",
                },
                "user_message": {
                    "type": "string",
                    "description": "Original user request for understanding the selection goal",
                },
                "selection_criteria": {
                    "type": "string",
                    "enum": ["best_method", "most_practical", "best_overall"],
                    "description": "Selection preference (default: best_overall)",
                },
            },
            "required": ["papers", "user_message"],
        },
    },
}


async def paper_select_best_skill(
    papers: list[dict] | None = None,
    comparison: dict | None = None,
    user_message: str = "",
    selection_criteria: str = "best_overall",
) -> dict:
    papers = papers or []
    trace_tool = TraceTool()
    semantic_memory = SemanticMemoryService()

    trace = trace_tool.create(task_type="select_best_paper", user_input=user_message)
    logger.info(
        f"[Skill:select_best trace={trace.trace_id}] n_candidates={len(papers)}, "
        f"criteria={selection_criteria}, comparison={comparison is not None}"
    )

    if len(papers) < 1:
        await trace_tool.complete(trace.trace_id, status="failed",
                                   error_message="No papers to select from", trace=trace)
        return {"success": False, "trace_id": trace.trace_id, "message": "没有候选论文可供选择。"}

    if len(papers) == 1:
        await trace_tool.complete(trace.trace_id, status="success", trace=trace)
        return {
            "success": True,
            "trace_id": trace.trace_id,
            "selected_paper": papers[0],
            "selection_reason": "唯一候选论文。",
            "tradeoff_summary": "单篇论文，无需权衡。",
        }

    preferences = await semantic_memory.load_user_preferences()

    if llm_client.available:
        result = await _llm_select(papers, comparison, user_message, selection_criteria, preferences, trace, trace_tool)
    else:
        result = _rule_select(papers, comparison, preferences)

    await trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="select_best",
        input_summary=f"candidates={len(papers)}, criteria={selection_criteria}",
        output_summary=f"selected={result.get('selected_paper', {}).get('arxiv_id', '') if result.get('selected_paper') else 'none'}, "
                       f"reason={result.get('selection_reason', '')[:80]}",
    )

    await trace_tool.complete(trace.trace_id, status="success", trace=trace)
    result["success"] = True
    result["trace_id"] = trace.trace_id
    return result


async def _llm_select(
    papers: list[dict],
    comparison: dict | None,
    user_message: str,
    selection_criteria: str,
    preferences: dict,
    trace,
    trace_tool: TraceTool,
) -> dict:
    paper_texts = []
    for i, paper in enumerate(papers, 1):
        title = paper.get("title", "")
        summary = paper.get("summary", paper.get("abstract", ""))
        core_problem = paper.get("core_problem", "")
        method = paper.get("method", "")
        result = paper.get("result", "")
        score = paper.get("final_score", paper.get("score", ""))
        paper_texts.append(
            f"Paper {i} (arxiv_id={paper.get('arxiv_id', '')}):\n"
            f"  Title: {title}\n"
            f"  Summary: {summary}\n"
            f"  Core Problem: {core_problem}\n"
            f"  Method: {method}\n"
            f"  Result: {result}\n"
            f"  Score: {score}\n"
        )

    comp_text = ""
    if comparison:
        comp_text = f"\nComparison Results:\n{comparison.get('overview', '')}\n"
        dims = comparison.get("dimensions", {})
        for dim_key, dim_text in dims.items():
            comp_text += f"\n{dim_key}:\n{dim_text[:500]}\n"

    preferred_topics = preferences.get("preferred_topics", [])

    prompt = (
        "Select the best paper from the following candidates based on the user's goal.\n\n"
        f"User request: {user_message}\n"
        f"Selection criteria: {selection_criteria}\n"
        f"User preferred topics: {preferred_topics}\n"
        f"{comp_text}\n"
        + "\n\n".join(paper_texts)
        + "\n\nReturn a JSON object with:\n"
        "- selected_arxiv_id: the arXiv ID of the best paper\n"
        "- selection_reason: detailed reason in Chinese (2-4 sentences)\n"
        "- tradeoff_summary: brief tradeoff summary in Chinese\n"
    )

    result = await llm_client.chat_json(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1024,
    )

    if result.get("success") and result.get("data"):
        data = result["data"]
        selected_id = data.get("selected_arxiv_id", "")
        for paper in papers:
            if paper.get("arxiv_id") == selected_id:
                return {
                    "selected_paper": paper,
                    "selection_reason": data.get("selection_reason", ""),
                    "tradeoff_summary": data.get("tradeoff_summary", ""),
                }
        logger.warning("LLM selected invalid arxiv_id, falling back to rule")

    return _rule_select(papers, comparison, preferences)


def _rule_select(papers: list[dict], comparison: dict | None, preferences: dict | None = None) -> dict:
    preferences = preferences or {}
    preferred_topics = [t.lower() for t in preferences.get("preferred_topics", [])]

    scored = []
    for paper in papers:
        score = 0.0
        # Use existing rerank score if present
        score += paper.get("final_score", paper.get("score", 0)) * 0.4

        # Topic match bonus
        title = (paper.get("title", "") + " " + paper.get("summary", "")).lower()
        topic_hits = sum(1 for t in preferred_topics if t.lower() in title)
        score += topic_hits * 0.15

        # Information completeness
        complete = 0
        if paper.get("core_problem"):
            complete += 1
        if paper.get("method"):
            complete += 1
        if paper.get("result"):
            complete += 1
        score += complete * 0.1

        # Summary source bonus (full_text > abstract_intro > metadata_only)
        source = paper.get("summary_source", "metadata_only")
        if source == "full_text":
            score += 0.15
        elif source == "abstract_intro":
            score += 0.05

        scored.append((paper, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    if comparison and comparison.get("dimensions"):
        # Try to pick based on comparison quality hints
        dims = comparison["dimensions"]
        value_text = dims.get("value", "")
        for p, s in scored:
            p_title = p.get("title", "")
            if p_title and p_title in value_text:
                # Paper explicitly praised in comparison value section
                return {
                    "selected_paper": p,
                    "selection_reason": f"根据对比分析的价值评估选择: {p_title}",
                    "tradeoff_summary": "基于对比分析的综合价值最高。",
                }

    best = scored[0][0] if scored else papers[0]
    return {
        "selected_paper": best,
        "selection_reason": f"综合评分最高 (rerank分数、主题匹配度、信息完整度): {best.get('title', '')}",
        "tradeoff_summary": "综合各项指标的最佳选择。",
    }
