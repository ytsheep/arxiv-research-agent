from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI, HTTPException

from app.api.contracts import (
    DigestRunResponse,
    DigestTriggerRequest,
    DigestTriggerResponse,
    SearchRequest,
    SearchResponse,
    SubscriptionCreateRequest,
    SubscriptionResponse,
    SubscriptionUpdateRequest,
)
from app.config import get_settings
from app.db import init_db
from app.services import DailyDigestService, SubscriptionService


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
digest_service = DailyDigestService(settings)
subscription_service = SubscriptionService(settings)
scheduler = BackgroundScheduler(timezone=settings.timezone)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    if settings.digest_enabled and not scheduler.running:
        scheduler.add_job(
            digest_service.run_due_subscriptions,
            trigger=IntervalTrigger(minutes=max(1, settings.scheduler_scan_interval_minutes)),
            id="digest-subscription-scanner",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        scheduler.start()
        logger.info(
            "Scheduler started. Scanning subscriptions every %s minute(s).",
            settings.scheduler_scan_interval_minutes,
        )
    try:
        yield
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)


app = FastAPI(
    title="arXiv Research Agent API",
    version="2.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "scheduler_enabled": settings.digest_enabled,
        "scan_interval_minutes": settings.scheduler_scan_interval_minutes,
        "timezone": settings.timezone,
    }


@app.post("/api/v1/research/search", response_model=SearchResponse)
def search_papers(payload: SearchRequest):
    try:
        result = digest_service.generate_digest(
            query=payload.query,
            keywords=payload.keywords,
            focus=payload.focus,
            top_k=payload.top_k,
            max_results=payload.max_results,
            api_key=payload.api_key,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return SearchResponse(
        query=result.query,
        focus=result.focus,
        markdown=result.markdown,
        papers=result.papers,
        tool_trace=result.tool_trace,
    )


@app.get("/api/v1/subscriptions", response_model=list[SubscriptionResponse])
def list_subscriptions():
    return subscription_service.list_subscriptions()


@app.post("/api/v1/subscriptions", response_model=SubscriptionResponse)
def create_subscription(payload: SubscriptionCreateRequest):
    try:
        return subscription_service.create_subscription(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/v1/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(subscription_id: int):
    try:
        return subscription_service.get_subscription_or_raise(subscription_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.put("/api/v1/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
def update_subscription(subscription_id: int, payload: SubscriptionUpdateRequest):
    try:
        return subscription_service.update_subscription(subscription_id, payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.delete("/api/v1/subscriptions/{subscription_id}")
def delete_subscription(subscription_id: int):
    try:
        subscription_service.delete_subscription(subscription_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"deleted": True, "subscription_id": subscription_id}


@app.get("/api/v1/subscriptions/{subscription_id}/runs", response_model=list[DigestRunResponse])
def list_subscription_runs(subscription_id: int):
    try:
        runs = subscription_service.list_runs(subscription_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [
        DigestRunResponse(
            id=run.id,
            subscription_id=run.subscription_id,
            trigger_mode=run.trigger_mode,
            scheduled_for_date=run.scheduled_for_date,
            status=run.status,
            papers_count=run.papers_count,
            error_message=run.error_message,
            started_at=run.started_at,
            finished_at=run.finished_at,
        )
        for run in runs
    ]


@app.post("/api/v1/subscriptions/{subscription_id}/run", response_model=DigestTriggerResponse)
def trigger_subscription(subscription_id: int, payload: DigestTriggerRequest):
    try:
        result = digest_service.run_subscription(
            subscription_id=subscription_id,
            notify=payload.notify,
            api_key=payload.api_key,
            trigger_mode="manual",
            scheduled_for_date=None,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return DigestTriggerResponse(
        subscription_id=result.subscription_id or subscription_id,
        subscription_name=result.subscription_name or "",
        query=result.query,
        focus=result.focus,
        papers_count=len(result.papers),
        notified_channels=result.notified_channels,
        generated_at=result.generated_at,
        delivery_results=result.delivery_results,
    )
