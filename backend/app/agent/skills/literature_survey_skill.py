"""Literature Survey Skill: search + summarize + compare to produce a survey."""

from app.agent.skills.paper_search_card_skill import paper_search_card_skill
from app.tools.llm_client import llm_client
from app.tools.trace_tool import TraceTool
from app.core.logging import logger

LITERATURE_SURVEY_SKILL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "literature_survey_skill",
        "description": "Search for papers on a topic, summarize them, and produce a small literature survey. Use this when the user asks for a survey, overview, or literature review of a topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_message": {
                    "type": "string",
                    "description": "The original user message",
                },
                "topic": {
                    "type": "string",
                    "description": "The research topic for the survey",
                },
                "top_n": {
                    "type": "integer",
                    "description": "Number of papers to include in the survey (default 5)",
                    "default": 5,
                },
                "candidate_k": {
                    "type": "integer",
                    "description": "Number of candidate papers to fetch from arXiv (default 30)",
                    "default": 30,
                },
            },
            "required": ["user_message", "topic"],
        },
    },
}


async def literature_survey_skill(
    user_message: str = "",
    topic: str = "",
    top_n: int = 5,
    candidate_k: int = 30,
) -> dict:
    trace_tool = TraceTool()

    trace = trace_tool.create(task_type="literature_survey", user_input=user_message)
    logger.info(f"[Skill:literature_survey trace={trace.trace_id}] topic={topic} top_n={top_n}")

    # Step 1: Expand query
    expanded_topic = _expand_topic(topic) if topic else "machine learning"
    await trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="query_rewrite",
        input_summary=f"original_topic={topic}",
        output_summary=f"expanded_topic={expanded_topic}",
    )

    # Step 2: Search papers
    search_result = await paper_search_card_skill(
        user_message=user_message,
        topic=expanded_topic,
        top_n=top_n,
        candidate_k=min(candidate_k, 50),
    )
    papers = search_result.get("papers", [])
    await trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="arxiv_search",
        input_summary=f"topic={expanded_topic}, top_n={top_n}",
        output_summary=f"found={len(papers)} papers",
    )

    if not papers:
        await trace_tool.complete(trace.trace_id, status="success", trace=trace)
        return {
            "success": True,
            "trace_id": trace.trace_id,
            "message": f'未找到与 "{topic}" 相关的论文，无法生成综述。',
            "survey_markdown": "",
            "papers": [],
        }

    # Step 3: Generate survey
    if llm_client.available:
        survey_md = await _llm_survey(topic, expanded_topic, papers)
    else:
        survey_md = _template_survey(topic, papers)

    await trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="generate_survey",
        input_summary=f"papers={len(papers)}",
        output_summary=f"survey_length={len(survey_md)} chars",
    )

    await trace_tool.complete(trace.trace_id, status="success", trace=trace)

    return {
        "success": True,
        "trace_id": trace.trace_id,
        "message": f"已完成关于 {topic} 的文献综述，共收录 {len(papers)} 篇论文",
        "survey_markdown": survey_md,
        "papers": papers,
    }


def _expand_topic(topic: str) -> str:
    """Simple heuristic query expansion for academic search."""
    expansions = {
        "agent": "autonomous agent multi-agent LLM agent task planning",
        "rag": "retrieval augmented generation RAG knowledge grounding",
        "llm": "large language model LLM alignment instruction tuning",
    }
    topic_lower = topic.lower()
    for key, expansion in expansions.items():
        if key in topic_lower:
            return f"{topic} {expansion}"
    return topic


async def _llm_survey(topic: str, expanded_topic: str, papers: list[dict]) -> str:
    paper_summaries = []
    for i, paper in enumerate(papers, 1):
        title = paper.get("title", "")
        summary = paper.get("summary", paper.get("abstract", ""))
        core_problem = paper.get("core_problem", "")
        method = paper.get("method", "")
        result = paper.get("result", "")
        paper_summaries.append(
            f"Paper {i}: {title}\n"
            f"Core problem: {core_problem}\n"
            f"Method: {method}\n"
            f"Result: {result}\n"
            f"Summary: {summary}"
        )

    prompt = (
        f"Write a short literature survey in Chinese about: {topic}\n\n"
        + "\n\n".join(paper_summaries)
        + "\n\nStructure the survey with these sections:\n"
        "## 1. 研究概览\n"
        "## 2. 关键主题与方法\n"
        "## 3. 代表性论文总结\n"
        "## 4. 研究空白与未来方向\n"
        "Use markdown. Keep it concise (~2000 words)."
    )

    result = await llm_client.chat(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=3000,
    )
    if result.get("success") and result.get("content"):
        return result["content"]
    return _template_survey(topic, papers)


def _template_survey(topic: str, papers: list[dict]) -> str:
    lines = [
        f"# 文献综述: {topic}\n",
        f"## 1. 研究概览\n",
        f"本次检索到 {len(papers)} 篇相关论文，涵盖 {topic} 方向的最新研究进展。\n",
        f"## 2. 代表性论文\n",
    ]
    for i, paper in enumerate(papers, 1):
        title = paper.get("title", "Unknown")
        arxiv_id = paper.get("arxiv_id", "")
        summary = paper.get("summary", paper.get("abstract", ""))
        core_problem = paper.get("core_problem", "详见论文")
        method = paper.get("method", "详见论文")
        result = paper.get("result", "详见论文")

        lines.append(f"### {i}. {title}\n")
        lines.append(f"- arXiv: {arxiv_id}\n")
        lines.append(f"- 核心问题: {core_problem}\n")
        lines.append(f"- 方法: {method}\n")
        lines.append(f"- 主要结果: {result}\n")
        lines.append(f"- 摘要: {summary[:300]}\n")

    lines.append(f"\n## 3. 研究空白与未来方向\n")
    lines.append(f"基于以上 {len(papers)} 篇论文的分析，该领域仍有多个值得探索的方向。建议深入阅读各论文的精读报告以获取更多细节。\n")

    return "\n".join(lines)
