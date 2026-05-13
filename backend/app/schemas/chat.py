from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str
    message: str


class PaperCardItem(BaseModel):
    arxiv_id: str
    title: str
    authors: list[str] = []
    published_date: str = ""
    categories: list[str] = []
    arxiv_url: str = ""
    pdf_url: str = ""
    summary: str = ""
    core_problem: str = ""
    method: str = ""
    result: str = ""
    summary_source: str = "metadata_only"
    actions: list[str] = ["collect", "parse", "view_pdf"]


class ChatResponse(BaseModel):
    success: bool = True
    type: str = ""
    trace_id: str = ""
    message: str = ""
    papers: list[PaperCardItem] = []
    error_code: str | None = None
    detail: str | None = None


class IntentResult(BaseModel):
    intent: str
    confidence: float
    entities: dict = {}
