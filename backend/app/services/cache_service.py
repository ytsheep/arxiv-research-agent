"""Cache service for arXiv search, embedding/rerank, and workflow state.

All cache operations are best-effort: failures never propagate.
Redis keys use a hash prefix to avoid collisions and include TTL jitter
to prevent stale-cache stampedes.
"""

from __future__ import annotations

import hashlib
import json
import random

from app.core.config import settings
from app.core.redis import redis_client
from app.core.logging import logger


def _make_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _jitter(base_seconds: int, pct: float = 0.15) -> int:
    """Add +/- pct jitter to avoid thundering herd on cache expiry."""
    delta = int(base_seconds * pct)
    return max(60, base_seconds + random.randint(-delta, delta))


class CacheService:
    """Thin cache facade. All methods return None on miss or error."""

    # ── arXiv search cache ────────────────────────────────────────────

    async def get_arxiv_search(self, query: str, candidate_k: int) -> list[dict] | None:
        key = f"arxiv:search:{_make_hash(query.strip().lower() + '|' + str(candidate_k))}"
        raw = await redis_client.get(key)
        if raw is None:
            return None
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                logger.debug(f"arXiv cache hit: {key}")
                return data
        except (json.JSONDecodeError, TypeError):
            await redis_client.delete(key)
        return None

    async def cache_arxiv_search(self, query: str, candidate_k: int, papers: list[dict]) -> None:
        ttl_minutes = random.randint(settings.redis_ttl_search_min, settings.redis_ttl_search_max)
        ttl = ttl_minutes * 60
        key = f"arxiv:search:{_make_hash(query.strip().lower() + '|' + str(candidate_k))}"
        try:
            ok = await redis_client.set(key, json.dumps(papers, ensure_ascii=False).encode(), ttl)
            if ok:
                logger.debug(f"arXiv cache write: {key} ttl={ttl_minutes}m")
        except Exception:
            pass

    # ── Embedding cache ───────────────────────────────────────────────

    async def get_embedding(self, text: str) -> list[float] | None:
        key = f"embedding:{_make_hash(text.strip())}"
        raw = await redis_client.get(key)
        if raw is None:
            return None
        try:
            data = json.loads(raw)
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], (int, float)):
                return data
        except (json.JSONDecodeError, TypeError):
            await redis_client.delete(key)
        return None

    async def cache_embedding(self, text: str, embedding: list[float]) -> None:
        ttl = settings.redis_ttl_embedding_days * 86400
        key = f"embedding:{_make_hash(text.strip())}"
        try:
            await redis_client.set(key, json.dumps(embedding).encode(), ttl)
        except Exception:
            pass

    # ── Rerank cache ──────────────────────────────────────────────────

    async def get_rerank(self, query: str, paper_ids: list[str], preference_version: str = "v1") -> list[dict] | None:
        ids_key = ",".join(sorted(paper_ids))
        raw_key = f"{query.strip().lower()}|{ids_key}|pref={preference_version}"
        key = f"rerank:{_make_hash(raw_key)}"
        raw = await redis_client.get(key)
        if raw is None:
            return None
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, TypeError):
            await redis_client.delete(key)
        return None

    async def cache_rerank(self, query: str, paper_ids: list[str], preference_version: str, result: list[dict]) -> None:
        ttl_minutes = random.randint(settings.redis_ttl_rerank_min, settings.redis_ttl_rerank_max)
        ttl = ttl_minutes * 60
        ids_key = ",".join(sorted(paper_ids))
        raw_key = f"{query.strip().lower()}|{ids_key}|pref={preference_version}"
        key = f"rerank:{_make_hash(raw_key)}"
        try:
            await redis_client.set(key, json.dumps(result, ensure_ascii=False).encode(), ttl)
        except Exception:
            pass

    # ── Workflow state cache ──────────────────────────────────────────

    async def get_workflow_state(self, workflow_id: str) -> dict | None:
        key = f"workflow:state:{workflow_id}"
        raw = await redis_client.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            await redis_client.delete(key)
        return None

    async def cache_workflow_state(self, workflow_id: str, projection: dict) -> None:
        ttl = settings.redis_ttl_workflow_hours * 3600
        key = f"workflow:state:{workflow_id}"
        try:
            await redis_client.set(key, json.dumps(projection, ensure_ascii=False).encode(), ttl)
        except Exception:
            pass


cache_service = CacheService()
