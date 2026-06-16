"""Chat service: handles chat messages and orchestrates paper search flow."""

from app.agent.shared import orchestrator
from app.schemas.chat import ChatResponse
from app.schemas.stream import ChatTaskAccepted, ProgressEvent
from app.services.progress_event_service import progress_event_service


async def handle_chat_message(message: str, session_id: str) -> ChatResponse:
    """Handle an incoming chat message."""
    return await orchestrator.handle_chat(message, session_id)


async def submit_chat_task(message: str, session_id: str) -> ChatTaskAccepted:
    trace = orchestrator.create_trace(message)
    trace_id = trace.trace_id
    await progress_event_service.publish(ProgressEvent(
        trace_id=trace_id,
        event_type="workflow.accepted",
        status="accepted",
        message="任务已接收，正在启动 Agent 工作流",
    ))
    progress_event_service.track_task(
        trace_id,
        _run_chat_task(message, session_id, trace),
    )
    return ChatTaskAccepted(
        trace_id=trace_id,
        stream_url=f"/api/chat/tasks/{trace_id}/events",
        result_url=f"/api/chat/tasks/{trace_id}/result",
    )


async def _run_chat_task(message: str, session_id: str, trace) -> None:
    try:
        response = await orchestrator.handle_chat(
            message=message,
            session_id=session_id,
            trace=trace,
            progress_callback=lambda state: progress_event_service.publish_state(
                trace.trace_id, state,
            ),
        )
        await progress_event_service.complete(trace.trace_id, response.model_dump())
    except Exception as exc:
        await progress_event_service.fail(trace.trace_id, f"任务执行失败: {exc}")
