"""Chat API routes."""

import json

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.stream import ChatTaskAccepted
from app.services.chat_service import handle_chat_message, submit_chat_task
from app.services.progress_event_service import progress_event_service

router = APIRouter()


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat messages. Main entry point for user interaction."""
    return await handle_chat_message(
        message=request.message,
        session_id=request.session_id,
    )


@router.post("/api/chat/tasks", response_model=ChatTaskAccepted, status_code=202)
async def create_chat_task(request: ChatRequest):
    return await submit_chat_task(
        message=request.message,
        session_id=request.session_id,
    )


@router.get("/api/chat/tasks/{trace_id}/events")
async def stream_chat_task(
    trace_id: str,
    last_event_id: str = Header("", alias="Last-Event-ID"),
):
    if not progress_event_service.is_known(trace_id):
        raise HTTPException(status_code=404, detail="Chat task not found")

    async def event_stream():
        async for event in progress_event_service.subscribe(trace_id, last_event_id):
            event_id = event.get("event_id", "")
            data = json.dumps(event, ensure_ascii=False)
            yield f"id: {event_id}\ndata: {data}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/api/chat/tasks/{trace_id}/result")
async def get_chat_task_result(trace_id: str):
    result = progress_event_service.get_result(trace_id)
    if result is not None:
        return {"success": True, "status": "completed", "data": result}
    if progress_event_service.is_known(trace_id):
        return JSONResponse(
            status_code=202,
            content={"success": True, "status": "running", "data": None},
        )
    raise HTTPException(status_code=404, detail="Chat task not found")
