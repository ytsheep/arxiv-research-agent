"""Library API routes."""

from fastapi import APIRouter, Query
from app.tools.library_tool import LibraryTool
from app.services.paper_service import parse_paper

router = APIRouter()


@router.get("/api/library/papers")
async def list_papers(
    keyword: str = Query(""),
    status: str = Query(""),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
):
    """List papers in local library with search and pagination."""
    library_tool = LibraryTool()
    result = await library_tool.search_papers(
        keyword=keyword,
        status=status,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
    )
    return {"success": result["success"], "total": result["total"], "papers": result["papers"]}


@router.get("/api/library/papers/{arxiv_id}")
async def get_paper(arxiv_id: str):
    """Get a single paper from library."""
    library_tool = LibraryTool()
    result = await library_tool.get_paper(arxiv_id)
    return {
        "success": result["success"],
        "paper": result.get("paper"),
        "files": result.get("files"),
        "message": result.get("error", ""),
    }


@router.delete("/api/library/papers/{arxiv_id}")
async def delete_paper(arxiv_id: str, hard: bool = Query(False)):
    """Delete a paper (soft delete by default)."""
    library_tool = LibraryTool()
    mode = "hard" if hard else "soft"
    result = await library_tool.delete_paper(arxiv_id, delete_mode=mode)
    return {
        "success": result["success"],
        "message": "删除成功" if result["success"] else result.get("error", ""),
    }


@router.get("/api/library/papers/{arxiv_id}/report")
async def get_report(arxiv_id: str):
    """Get parsed report markdown for a paper."""
    library_tool = LibraryTool()
    result = await library_tool.get_report(arxiv_id)
    return {
        "success": result["success"],
        "report_markdown": result.get("report_markdown", ""),
        "message": result.get("error", ""),
    }


@router.delete("/api/library/papers/{arxiv_id}/report")
async def delete_report(arxiv_id: str):
    """Delete report and parsed files for a paper."""
    library_tool = LibraryTool()
    result = await library_tool.delete_report(arxiv_id)
    return {
        "success": result["success"],
        "message": "报告已删除" if result["success"] else result.get("error", ""),
    }


@router.post("/api/library/papers/{arxiv_id}/report/regenerate")
async def regenerate_report(arxiv_id: str):
    """Regenerate report by re-parsing the paper."""
    return await parse_paper(arxiv_id)
