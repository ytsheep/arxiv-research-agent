from pydantic import BaseModel, field_validator


class PaperMetadata(BaseModel):
    arxiv_id: str = ""
    title: str = ""
    authors: list[str] = []
    abstract: str = ""
    categories: list[str] = []
    published_date: str = ""
    updated_date: str = ""
    arxiv_url: str = ""
    pdf_url: str = ""

    # Accept camelCase from frontend
    @field_validator("arxiv_id", mode="before")
    @classmethod
    def coerce_arxiv_id(cls, v):
        return v if v else ""

    @field_validator("published_date", mode="before")
    @classmethod
    def coerce_published_date(cls, v):
        return v if v else ""


class PaperCollectRequest(BaseModel):
    paper: dict | None = None


class PaperItem(BaseModel):
    arxiv_id: str
    title: str
    authors: list[str] = []
    abstract: str = ""
    categories: list[str] = []
    published_date: str = ""
    arxiv_url: str = ""
    pdf_url: str = ""
    source: str = ""
    status: str = "collected"
    has_pdf: bool = False
    has_parsed_doc: bool = False
    has_report: bool = False
    tags: list[str] = []
    created_at: str = ""


class PaperListResponse(BaseModel):
    success: bool = True
    total: int = 0
    papers: list[PaperItem] = []


class PaperDetailResponse(BaseModel):
    success: bool = True
    paper: PaperItem | None = None
    summary: dict | None = None
    files: dict | None = None


class OperationResponse(BaseModel):
    success: bool = True
    trace_id: str = ""
    status: str = ""
    message: str = ""
    error_code: str | None = None
    detail: str | None = None
