"""MCP prompts for paper summary and report generation."""

from app.agent.prompts import (
    CARD_SUMMARY_SYSTEM,
    build_card_summary_prompt,
    DEEP_REPORT_SYSTEM,
)

PAPER_PROMPTS = {
    "paper/card_summary_zh": {
        "description": "Generate a Chinese paper card summary from title and abstract. Uses LLM when available, regex fallback otherwise. Does NOT access full text.",
        "arguments": [
            {"name": "title", "description": "Paper title", "required": True},
            {"name": "abstract", "description": "Paper abstract text", "required": True},
            {"name": "query", "description": "User's research topic for relevance context", "required": False},
        ],
    },
    "paper/deep_report_zh": {
        "description": "Generate a full Chinese deep reading report from a paper's parsed full text.",
        "arguments": [
            {"name": "title", "description": "Paper title", "required": True},
            {"name": "authors", "description": "Paper authors", "required": False},
            {"name": "parsed_markdown", "description": "Full text of the paper in markdown", "required": True},
        ],
    },
}


def get_paper_prompt(name: str, arguments: dict) -> dict:
    """Build prompt messages for a given prompt name."""
    if name == "paper/card_summary_zh":
        title = arguments.get("title", "")
        abstract = arguments.get("abstract", "")
        query = arguments.get("query", "")
        user_content = build_card_summary_prompt(title=title, abstract=abstract, query=query)
        return {
            "messages": [
                {"role": "system", "content": {"type": "text", "text": CARD_SUMMARY_SYSTEM}},
                {"role": "user", "content": {"type": "text", "text": user_content}},
            ],
        }

    if name == "paper/deep_report_zh":
        title = arguments.get("title", "")
        authors = arguments.get("authors", "")
        parsed = arguments.get("parsed_markdown", "")[:8000]
        user_content = f"论文标题：{title}\n作者：{authors}\n\n论文全文内容（节选）：\n{parsed}\n\n请基于以上内容生成中文精读报告。"
        return {
            "messages": [
                {"role": "system", "content": {"type": "text", "text": DEEP_REPORT_SYSTEM}},
                {"role": "user", "content": {"type": "text", "text": user_content}},
            ],
        }

    return {"messages": [{"role": "user", "content": {"type": "text", "text": f"Unknown prompt: {name}"}}]}
