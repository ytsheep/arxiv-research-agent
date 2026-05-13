"""Papers API routes."""

from fastapi import APIRouter, Request
from app.schemas.paper import OperationResponse
from app.services.paper_service import collect_paper, parse_paper

router = APIRouter()


def _camel_to_snake(paper_dict: dict) -> dict:
    """Convert camelCase keys from frontend to snake_case for backend."""
    key_map = {
        "arxivId": "arxiv_id",
        "publishedDate": "published_date",
        "updatedDate": "updated_date",
        "arxivUrl": "arxiv_url",
        "pdfUrl": "pdf_url",
        "summarySource": "summary_source",
        "coreProblem": "core_problem",
    }
    result = {}
    for k, v in paper_dict.items():
        new_key = key_map.get(k, k)
        result[new_key] = v
    return result


@router.post("/api/papers/{arxiv_id}/collect", response_model=OperationResponse)
async def collect_paper_endpoint(arxiv_id: str, request: Request):
    """Collect a paper: download PDF, save metadata, write to local library."""
    body = await request.json()
    paper_raw = body.get("paper", {}) if isinstance(body, dict) else {}
    paper_metadata = _camel_to_snake(paper_raw) if paper_raw else None
    return await collect_paper(arxiv_id, paper_metadata)


@router.post("/api/papers/{arxiv_id}/parse", response_model=OperationResponse)
async def parse_paper_endpoint(arxiv_id: str):
    """Parse a paper: full text extraction and Chinese report generation."""
    return await parse_paper(arxiv_id)
