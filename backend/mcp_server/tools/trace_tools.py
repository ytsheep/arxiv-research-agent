"""MCP tools for trace/task observability."""

import json

TRACE_TOOLS = {
    "trace.query": {
        "description": "Query task execution traces. Search by keyword, task type, status, or tags.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Search in user_input or summary"},
                "task_type": {"type": "string", "description": "Filter by type: chat, paper_search, paper_parse, subscription_run"},
                "status": {"type": "string", "description": "Filter: running, success, failed"},
                "page": {"type": "integer", "description": "Page number (default 1)"},
                "page_size": {"type": "integer", "description": "Results per page (default 20)"},
            },
        },
    },
    "trace.get": {
        "description": "Get a full trace with all steps by trace_id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "trace_id": {"type": "string", "description": "Trace ID e.g. 'trace_20260512_0001'"},
            },
            "required": ["trace_id"],
        },
    },
}


async def call_trace_tool(name: str, arguments: dict) -> dict:
    from app.tools.trace_tool import TraceTool

    tool = TraceTool()

    if name == "trace.query":
        result = await tool.query(
            keyword=arguments.get("keyword", ""),
            task_type=arguments.get("task_type", ""),
            status=arguments.get("status", ""),
            page=arguments.get("page", 1),
            page_size=arguments.get("page_size", 20),
        )
    elif name == "trace.get":
        result = await tool.get(
            trace_id=arguments.get("trace_id", ""),
        )
        if result is None:
            result = {"success": False, "error": "Trace not found"}
        else:
            result = {"success": True, "trace": result}
    else:
        result = {"success": False, "error": f"Unknown tool: {name}"}

    text = json.dumps(result, ensure_ascii=False, indent=2)
    return {
        "content": [{"type": "text", "text": text}],
        "isError": not result.get("success", True),
    }
