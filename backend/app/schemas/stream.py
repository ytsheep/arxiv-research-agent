from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProgressEvent(BaseModel):
    event_id: str = ""
    trace_id: str
    event_type: str
    agent: str = ""
    node: str = ""
    task_id: str = ""
    task_type: str = ""
    status: str = "running"
    message: str
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ChatTaskAccepted(BaseModel):
    success: bool = True
    trace_id: str
    status: str = "accepted"
    stream_url: str
    result_url: str
