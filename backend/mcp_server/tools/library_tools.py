"""MCP tools for local paper library management."""

import json

LIBRARY_TOOLS = {
    "library.search_papers": {
        "description": "Search the local paper library by keyword, status, or pagination.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Keyword to search in titles/abstracts"},
                "status": {"type": "string", "description": "Filter by status: collected, parsed, deleted"},
                "page": {"type": "integer", "description": "Page number (default 1)"},
                "page_size": {"type": "integer", "description": "Results per page (default 20)"},
            },
        },
    },
    "library.get_report": {
        "description": "Get the Chinese deep reading report for a paper in the local library.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "arxiv_id": {"type": "string", "description": "arXiv ID e.g. '2401.15391v1'"},
            },
            "required": ["arxiv_id"],
        },
    },
    "library.get_paper": {
        "description": "Get detailed info (metadata, file paths, tags) for a paper in the local library.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "arxiv_id": {"type": "string", "description": "arXiv ID"},
            },
            "required": ["arxiv_id"],
        },
    },
}


async def call_library_tool(name: str, arguments: dict) -> dict:
    from app.tools.library_tool import LibraryTool

    tool = LibraryTool()

    if name == "library.search_papers":
        result = await tool.search_papers(
            keyword=arguments.get("keyword", ""),
            status=arguments.get("status", ""),
            page=arguments.get("page", 1),
            page_size=arguments.get("page_size", 20),
        )
    elif name == "library.get_report":
        result = await tool.get_report(
            arxiv_id=arguments.get("arxiv_id", ""),
        )
    elif name == "library.get_paper":
        result = await tool.get_paper(
            arxiv_id=arguments.get("arxiv_id", ""),
        )
    else:
        result = {"success": False, "error": f"Unknown tool: {name}"}

    text = json.dumps(result, ensure_ascii=False, indent=2)
    return {
        "content": [{"type": "text", "text": text}],
        "isError": not result.get("success", True),
    }
