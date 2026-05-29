"""AgentMessage: structured in-process message for multi-agent communication."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: f"msg_{uuid4().hex[:12]}")
    workflow_id: str = ""
    task_id: str = ""
    sender: str  # "supervisor" | "executor" | "reviewer"
    receiver: str
    message_type: str  # see MESSAGE_TYPES below
    payload: dict = {}
    metadata: dict = {}
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


MESSAGE_TYPES = {
    "user.request": "Initial request from orchestrator to supervisor",
    "task.planned": "Supervisor announces task plan",
    "task.assigned": "Supervisor dispatches a task to executor",
    "task.result": "Executor returns task result",
    "task.reviewed": "Reviewer sends decision to supervisor",
    "workflow.final": "Supervisor declares workflow complete",
    "workflow.error": "Any agent reports an irrecoverable error",
}
