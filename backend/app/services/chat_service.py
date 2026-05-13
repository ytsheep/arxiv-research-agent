"""Chat service: handles chat messages and orchestrates paper search flow."""

from app.agent.shared import orchestrator
from app.schemas.chat import ChatResponse


async def handle_chat_message(message: str, session_id: str) -> ChatResponse:
    """Handle an incoming chat message."""
    return await orchestrator.handle_chat(message, session_id)
