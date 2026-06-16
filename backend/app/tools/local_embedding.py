"""Local BGE-M3 embedding service. Uses sentence-transformers for zero-API-call embeddings."""

from __future__ import annotations
import asyncio
import math
import threading
import time

from app.core.config import settings
from app.core.logging import logger

_embedding_model = None
_model_lock = threading.Lock()
_model_status = {
    "model": settings.bge_model_path,
    "status": "not_loaded",
    "warmup_duration_ms": 0,
    "error": "",
}


def _load_model():
    global _embedding_model
    if _embedding_model is not None:
        return _embedding_model
    if _model_status.get("status") == "degraded":
        return None
    with _model_lock:
        if _embedding_model is not None:
            return _embedding_model
        _model_status.update({"status": "loading", "error": ""})
        try:
            from sentence_transformers import SentenceTransformer
            model_name = settings.bge_model_path
            logger.info(f"Loading local embedding model: {model_name}")
            _embedding_model = SentenceTransformer(model_name)
            _model_status.update({"status": "ready", "error": ""})
            logger.info(f"Local embedding model loaded: {model_name}")
        except ImportError:
            logger.warning("sentence-transformers not installed, embedding unavailable")
            _model_status.update({
                "status": "degraded",
                "error": "sentence-transformers not installed",
            })
            _embedding_model = None
        except Exception as exc:
            logger.error(f"Failed to load local embedding model: {exc}")
            _model_status.update({"status": "degraded", "error": str(exc)})
            _embedding_model = None
    return _embedding_model


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Encode a batch of texts into dense vectors using BGE-M3. Returns empty list on failure."""
    model = _load_model()
    if model is None:
        return []
    try:
        embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return [emb.tolist() for emb in embeddings]
    except Exception as exc:
        logger.error(f"Local embedding failed: {exc}")
        return []


def embed_single(text: str) -> list[float]:
    """Encode a single text. Returns empty list on failure."""
    batch = embed_batch([text])
    return batch[0] if batch else []


def is_available() -> bool:
    """Check if local embedding model is loaded and ready."""
    return _load_model() is not None


async def warmup() -> dict:
    """Load BGE-M3 and run one inference before accepting user traffic."""
    started = time.perf_counter()
    if not settings.bge_preload_enabled:
        _model_status.update({"status": "disabled", "warmup_duration_ms": 0, "error": ""})
        return get_status()

    try:
        vector = await asyncio.to_thread(embed_single, "BGE-M3 startup warmup")
        duration_ms = int((time.perf_counter() - started) * 1000)
        _model_status["warmup_duration_ms"] = duration_ms
        if vector:
            _model_status.update({"status": "ready", "error": ""})
            logger.info(f"BGE-M3 warmup completed in {duration_ms} ms")
        else:
            _model_status.update({"status": "degraded", "error": "Warmup returned no embedding"})
            logger.warning("BGE-M3 warmup returned no embedding; TF-IDF fallback remains available")
    except Exception as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        _model_status.update({
            "status": "degraded",
            "warmup_duration_ms": duration_ms,
            "error": str(exc),
        })
        logger.error(f"BGE-M3 warmup failed: {exc}")
    return get_status()


def get_status() -> dict:
    return dict(_model_status)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors (assumes normalized)."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
