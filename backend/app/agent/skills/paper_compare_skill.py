"""Paper Compare Skill: load multiple papers and compare across dimensions."""

from app.tools.library_tool import LibraryTool
from app.tools.llm_client import llm_client
from app.tools.trace_tool import TraceTool
from app.services.memory_service import ShortTermMemoryService
from app.core.logging import logger

PAPER_COMPARE_SKILL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "paper_compare_skill",
        "description": "Compare multiple papers across problem, method, experiment, result, limitation, and value dimensions. Use this when the user wants to compare or contrast papers.",
        "parameters": {
            "type": "object",
            "properties": {
                "arxiv_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of arXiv paper IDs to compare",
                },
                "user_message": {
                    "type": "string",
                    "description": "The original user message for context",
                },
            },
            "required": ["arxiv_ids", "user_message"],
        },
    },
}


async def paper_compare_skill(
    arxiv_ids: list[str] | None = None,
    user_message: str = "",
) -> dict:
    arxiv_ids = arxiv_ids or []
    trace_tool = TraceTool()
    library_tool = LibraryTool()

    trace = trace_tool.create(task_type="paper_compare", user_input=user_message)
    logger.info(f"[Skill:paper_compare trace={trace.trace_id}] ids={arxiv_ids}")

    if len(arxiv_ids) < 2:
        await trace_tool.complete(trace.trace_id, status="failed",
                                   error_message="Need at least 2 papers to compare", trace=trace)
        return {
            "success": False,
            "trace_id": trace.trace_id,
            "message": "需要至少 2 篇论文才能进行对比。",
        }

    # Load paper data
    papers_data = []
    for arxiv_id in arxiv_ids:
        paper_result = await library_tool.get_paper(arxiv_id)
        if paper_result.get("success"):
            paper_info = paper_result.get("paper", {})
            report_result = await library_tool.get_report(arxiv_id)
            paper_info["report_markdown"] = report_result.get("report_markdown", "")
            paper_info["has_report"] = report_result.get("success", False)
            papers_data.append(paper_info)
        else:
            papers_data.append({
                "arxiv_id": arxiv_id,
                "title": arxiv_id,
                "report_markdown": "",
                "has_report": False,
            })

    await trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="resolve_papers",
        input_summary=f"arxiv_ids={arxiv_ids}",
        output_summary=f"loaded={len(papers_data)} papers, with_report={sum(1 for p in papers_data if p.get('has_report'))}",
    )

    # Build comparison
    if llm_client.available:
        comparison = await _llm_compare(papers_data)
    else:
        comparison = _template_compare(papers_data)

    await trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="compare_papers",
        input_summary=f"papers={len(papers_data)}",
        output_summary=f"dimensions={list(comparison.get('dimensions', {}).keys())}",
    )

    await trace_tool.complete(trace.trace_id, status="success", trace=trace)

    return {
        "success": True,
        "trace_id": trace.trace_id,
        "message": f"已完成 {len(papers_data)} 篇论文对比分析",
        "comparison": comparison,
    }


async def _llm_compare(papers: list[dict]) -> dict:
    paper_texts = []
    for i, paper in enumerate(papers, 1):
        title = paper.get("title", "")
        summary = paper.get("summary", paper.get("abstract", ""))
        report = paper.get("report_markdown", "")[:2000]
        paper_texts.append(f"Paper {i}: {title}\nSummary: {summary}\nReport excerpt: {report}")

    prompt = (
        "Compare the following papers across these dimensions: "
        "problem (research question addressed), method (approach/technique used), "
        "experiment (datasets, baselines, metrics), result (key findings), "
        "limitation (acknowledged weaknesses), value (practical/scientific contribution).\n\n"
        + "\n\n".join(paper_texts)
        + "\n\nReturn a JSON object with keys: overview (one-sentence comparison), "
        "papers (list of {arxiv_id, title}), dimensions (object with keys problem/method/experiment/result/limitation/value, "
        "each containing a comparative analysis text). Use Chinese."
    )

    result = await llm_client.chat_json(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2048,
    )
    if result.get("success") and result.get("data"):
        return result["data"]

    return _template_compare(papers)


def _template_compare(papers: list[dict]) -> dict:
    dimensions = {
        "problem": "",
        "method": "",
        "experiment": "",
        "result": "",
        "limitation": "",
        "value": "",
    }
    papers_out = []
    for paper in papers:
        arxiv_id = paper.get("arxiv_id", "")
        title = paper.get("title", arxiv_id)
        papers_out.append({"arxiv_id": arxiv_id, "title": title})

        summary = paper.get("summary", paper.get("abstract", ""))
        dimensions["problem"] += f"**{title}**: {paper.get('core_problem', '详见论文')}\n\n"
        dimensions["method"] += f"**{title}**: {paper.get('method', '详见论文')}\n\n"
        dimensions["result"] += f"**{title}**: {paper.get('result', '详见论文')}\n\n"
        dimensions["limitation"] += f"**{title}**: {paper.get('limitation_summary', '未明确说明')}\n\n"
        dimensions["value"] += f"**{title}**: 基于摘要的贡献评估\n\n"

    dimensions["experiment"] = "需要全文解析报告以提供详细实验对比。"
    if not any(dimensions.get(k) for k in ["problem", "method", "result"] if k != "experiment"):
        for k in dimensions:
            if not dimensions[k]:
                dimensions[k] = "无可用的对比信息。请先解析论文以获取更多细节。"

    return {
        "overview": f"对比了 {len(papers)} 篇论文",
        "papers": papers_out,
        "dimensions": dimensions,
    }
