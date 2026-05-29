"""MessageBus: local in-memory message bus backed by WorkflowState.message_history.

This is NOT a network bus. Messages are appended to the state's
message_history list and persisted by the LangGraph Checkpointer.
"""

from __future__ import annotations

from app.agent.message_schema import AgentMessage


class MessageBus:
    """Static helper for reading/writing messages in WorkflowState."""

    @staticmethod
    def publish(state: dict, msg: AgentMessage) -> list[dict]:
        """Append a message to state.message_history and return the updated list."""
        msgs = list(state.get("message_history", []))
        msgs.append(msg.model_dump())
        # Keep only the most recent 100 messages
        if len(msgs) > 100:
            msgs = msgs[-100:]
        return msgs

    @staticmethod
    def get_messages_for_task(state: dict, task_id: str) -> list[dict]:
        return [m for m in state.get("message_history", []) if m.get("task_id") == task_id]

    @staticmethod
    def get_last_message_of_type(state: dict, msg_type: str) -> dict | None:
        msgs = state.get("message_history", [])
        for m in reversed(msgs):
            if m.get("message_type") == msg_type:
                return m
        return None

    @staticmethod
    def get_last_plan(state: dict) -> dict | None:
        return MessageBus.get_last_message_of_type(state, "task.planned")

    @staticmethod
    def get_last_task_result(state: dict, task_id: str) -> dict | None:
        msgs = MessageBus.get_messages_for_task(state, task_id)
        for m in reversed(msgs):
            if m.get("message_type") == "task.result":
                return m
        return None
