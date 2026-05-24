"""MCP Server: exposes project capabilities via Model Context Protocol (JSON-RPC over stdio).

Thin adapters that reuse existing app/tools and app/services — no business logic duplication.

Protocol: JSON-RPC 2.0 over stdin/stdout
Methods: tools/list, tools/call, resources/list, resources/read, prompts/list, prompts/get
"""

import sys
import json
import asyncio
from typing import Any

# Tool handlers
from mcp_server.tools.arxiv_tools import ARXIV_TOOLS, call_arxiv_tool
from mcp_server.tools.library_tools import LIBRARY_TOOLS, call_library_tool
from mcp_server.tools.trace_tools import TRACE_TOOLS, call_trace_tool

# Resource handlers
from mcp_server.resources.library_resources import LIBRARY_RESOURCES, read_library_resource
from mcp_server.resources.trace_resources import TRACE_RESOURCES, read_trace_resource

# Prompt handlers
from mcp_server.prompts.paper_prompts import PAPER_PROMPTS, get_paper_prompt

ALL_TOOLS = {**ARXIV_TOOLS, **LIBRARY_TOOLS, **TRACE_TOOLS}
ALL_RESOURCES = {**LIBRARY_RESOURCES, **TRACE_RESOURCES}
ALL_PROMPTS = {**PAPER_PROMPTS}


def handle_tools_list() -> dict:
    return {
        "tools": [
            {"name": name, "description": t["description"], "inputSchema": t["inputSchema"]}
            for name, t in ALL_TOOLS.items()
        ]
    }


async def handle_tools_call(name: str, arguments: dict) -> dict:
    if name in ARXIV_TOOLS:
        return await call_arxiv_tool(name, arguments)
    if name in LIBRARY_TOOLS:
        return await call_library_tool(name, arguments)
    if name in TRACE_TOOLS:
        return await call_trace_tool(name, arguments)
    return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True}


def handle_resources_list() -> dict:
    return {
        "resources": [
            {"uri": uri, "name": r["name"], "description": r.get("description", ""), "mimeType": r.get("mimeType", "text/plain")}
            for uri, r in ALL_RESOURCES.items()
        ]
    }


async def handle_resources_read(uri: str) -> dict:
    if uri in LIBRARY_RESOURCES:
        return await read_library_resource(uri)
    if uri in TRACE_RESOURCES:
        return await read_trace_resource(uri)
    return {"contents": [{"uri": uri, "text": "Resource not found", "mimeType": "text/plain"}]}


def handle_prompts_list() -> dict:
    return {
        "prompts": [
            {"name": name, "description": p["description"], "arguments": p.get("arguments", [])}
            for name, p in ALL_PROMPTS.items()
        ]
    }


def handle_prompts_get(name: str, arguments: dict) -> dict:
    if name in PAPER_PROMPTS:
        return get_paper_prompt(name, arguments)
    return {"messages": [{"role": "user", "content": {"type": "text", "text": f"Unknown prompt: {name}"}}]}


def process_request(request: dict) -> dict:
    """Synchronous router for JSON-RPC requests (dispatches async handlers)."""
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id")

    try:
        if method == "tools/list":
            result = handle_tools_list()
        elif method == "tools/call":
            result = asyncio.run(handle_tools_call(params.get("name", ""), params.get("arguments", {})))
        elif method == "resources/list":
            result = handle_resources_list()
        elif method == "resources/read":
            result = asyncio.run(handle_resources_read(params.get("uri", "")))
        elif method == "prompts/list":
            result = handle_prompts_list()
        elif method == "prompts/get":
            result = handle_prompts_get(params.get("name", ""), params.get("arguments", {}))
        elif method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
                "serverInfo": {"name": "arxiv-paper-agent-mcp", "version": "1.0.0"},
            }
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    except Exception as e:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}}


def main():
    """MCP Server entry point — reads JSON-RPC from stdin, writes to stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = process_request(request)
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            continue


if __name__ == "__main__":
    main()
