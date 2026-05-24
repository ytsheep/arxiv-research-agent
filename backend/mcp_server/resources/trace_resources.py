"""MCP resources for task execution traces."""

import json

TRACE_RESOURCES: dict[str, dict] = {
    "trace://recent": {
        "name": "Recent Traces",
        "description": "Most recent 10 task execution traces.",
        "mimeType": "application/json",
    },
    "trace://failed": {
        "name": "Failed Traces",
        "description": "All failed task execution traces (latest 20).",
        "mimeType": "application/json",
    },
    "trace://{trace_id}": {
        "name": "Trace Detail",
        "description": "Full trace with all steps for a specific trace ID. Replace {trace_id} with the actual ID.",
        "mimeType": "application/json",
    },
}


async def read_trace_resource(uri: str) -> dict:
    """Read trace resources by URI."""
    from app.tools.trace_tool import TraceTool

    tool = TraceTool()

    if uri == "trace://recent":
        result = await tool.query(page=1, page_size=10)
        text = json.dumps(result, ensure_ascii=False, indent=2)
        return {"contents": [{"uri": uri, "text": text, "mimeType": "application/json"}]}

    if uri == "trace://failed":
        result = await tool.query(status="failed", page=1, page_size=20)
        text = json.dumps(result, ensure_ascii=False, indent=2)
        return {"contents": [{"uri": uri, "text": text, "mimeType": "application/json"}]}

    # trace://{trace_id}
    if uri.startswith("trace://"):
        trace_id = uri[len("trace://"):]
        trace = await tool.get(trace_id)
        if trace:
            text = json.dumps(trace, ensure_ascii=False, indent=2)
            return {"contents": [{"uri": uri, "text": text, "mimeType": "application/json"}]}
        return {"contents": [{"uri": uri, "text": f"Trace not found: {trace_id}", "mimeType": "text/plain"}]}

    return {"contents": [{"uri": uri, "text": f"Unrecognized trace URI: {uri}", "mimeType": "text/plain"}]}
