"""arXiv Paper Agent - FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.papers import router as papers_router
from app.api.library import router as library_router
from app.api.subscriptions import router as subscriptions_router
from app.api.traces import router as traces_router
from app.api.settings import router as settings_router
from app.db.database import init_db
from app.jobs.scheduler import start_scheduler, shutdown_scheduler
from app.core.logging import logger
from app.agent.shared import orchestrator
from app.services.progress_event_service import progress_event_service
from app.tools.local_embedding import get_status as get_embedding_status
from app.tools.local_embedding import warmup as warmup_embedding


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting arXiv Paper Agent...")
    await init_db()
    logger.info("Database initialized")
    await warmup_embedding()
    await start_scheduler()
    logger.info("Scheduler started")
    yield
    shutdown_scheduler()
    await progress_event_service.close()
    await orchestrator.close()
    logger.info("Shutting down...")


app = FastAPI(
    title="arXiv Paper Agent",
    description="arXiv 论文助手 Agent API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(papers_router)
app.include_router(library_router)
app.include_router(subscriptions_router)
app.include_router(traces_router)
app.include_router(settings_router)


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "version": "0.1.0",
        "embedding": get_embedding_status(),
    }
