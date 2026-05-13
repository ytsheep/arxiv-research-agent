from pydantic import BaseModel


class TraceStep(BaseModel):
    step_name: str
    tool_name: str | None = None
    input_summary: str = ""
    output_summary: str = ""
    status: str = ""
    started_at: str = ""
    ended_at: str = ""
    duration_ms: int | None = None
    error_message: str = ""


class TraceItem(BaseModel):
    trace_id: str
    task_type: str
    user_input: str = ""
    summary: str = ""
    tags: list[str] = []
    status: str = ""
    started_at: str = ""
    ended_at: str = ""
    duration_ms: int | None = None
    error_message: str = ""
    steps: list[TraceStep] = []


class TraceListResponse(BaseModel):
    success: bool = True
    total: int = 0
    traces: list[TraceItem] = []


class TraceDetailResponse(BaseModel):
    success: bool = True
    trace: TraceItem | None = None
