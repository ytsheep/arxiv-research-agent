"""MCP tools for arXiv paper search and metadata."""

import json

ARXIV_TOOLS = {
    "arxiv.search_papers": {
        "description": "Search arXiv for papers matching a research topic query. Returns paper metadata (title, authors, abstract). Does NOT download PDFs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Research topic or keywords"},
                "max_results": {"type": "integer", "description": "Max candidates (default 20, max 50)"},
                "categories": {"type": "array", "items": {"type": "string"}, "description": "arXiv categories e.g. ['cs.AI']"},
            },
            "required": ["query"],
        },
    },
    "arxiv.get_paper_metadata": {
        "description": "Get metadata for a single paper by arXiv ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "arxiv_id": {"type": "string", "description": "arXiv ID e.g. '2401.15391v1'"},
            },
            "required": ["arxiv_id"],
        },
    },
}


async def call_arxiv_tool(name: str, arguments: dict) -> dict:
    from app.tools.arxiv_tool import ArxivTool

    tool = ArxivTool()

    if name == "arxiv.search_papers":
        result = await tool.search(
            query=arguments.get("query", ""),
            max_results=arguments.get("max_results", 20),
            categories=arguments.get("categories"),
        )
    elif name == "arxiv.get_paper_metadata":
        result = await tool.get_paper_metadata(
            arxiv_id=arguments.get("arxiv_id", ""),
        )
    else:
        result = {"success": False, "error": f"Unknown tool: {name}"}

    await tool.close()
    text = json.dumps(result, ensure_ascii=False, indent=2)
    return {
        "content": [{"type": "text", "text": text}],
        "isError": not result.get("success", True),
    }
