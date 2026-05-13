"""Chat API routes."""

from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import handle_chat_message

router = APIRouter()


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat messages. Main entry point for user interaction."""
    return await handle_chat_message(
        message=request.message,
        session_id=request.session_id,
    )
