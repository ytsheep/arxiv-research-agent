"""Trace service: query trace records."""

from app.agent.shared import orchestrator
from app.services.trace_projection_service import TraceProjectionService


async def query_traces(**kwargs) -> dict:
    result = await orchestrator.trace_tool.query(**kwargs)
    projector = TraceProjectionService(
        history_provider=orchestrator.get_state_history,
        trace_tool=orchestrator.trace_tool,
    )
    for trace in result.get("traces", []):
        if not trace.get("step_count"):
            trace["step_count"] = await projector.count_steps(trace["trace_id"])
    return result


async def get_trace(trace_id: str) -> dict | None:
    projector = TraceProjectionService(
        history_provider=orchestrator.get_state_history,
        trace_tool=orchestrator.trace_tool,
    )
    return await projector.get_trace(trace_id)
