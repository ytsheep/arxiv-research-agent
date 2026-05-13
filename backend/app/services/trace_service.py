"""Trace service: query trace records."""

from app.agent.shared import orchestrator


async def query_traces(**kwargs) -> dict:
    return await orchestrator.trace_tool.query(**kwargs)


async def get_trace(trace_id: str) -> dict | None:
    return await orchestrator.trace_tool.get(trace_id)
