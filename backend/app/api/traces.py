"""Trace API routes."""

from fastapi import APIRouter, Query
from app.services.trace_service import query_traces, get_trace

router = APIRouter()


@router.get("/api/traces")
async def list_traces(
    keyword: str = Query(""),
    task_type: str = Query(""),
    status: str = Query(""),
    tag: str = Query(""),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    result = await query_traces(
        keyword=keyword,
        task_type=task_type,
        status=status,
        tag=tag,
        page=page,
        page_size=page_size,
    )
    return {"success": True, **result}


@router.get("/api/traces/{trace_id}")
async def get_trace_detail(trace_id: str):
    trace = await get_trace(trace_id)
    if trace is None:
        return {"success": False, "trace": None, "message": "Trace not found"}
    return {"success": True, "trace": trace}
