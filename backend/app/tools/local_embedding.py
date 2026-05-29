"""Local BGE-M3 embedding service. Uses sentence-transformers for zero-API-call embeddings."""

from __future__ import annotations
import math
from app.core.logging import logger

_embedding_model = None


def _load_model():
    global _embedding_model
    if _embedding_model is not None:
        return _embedding_model
    try:
        from sentence_transformers import SentenceTransformer
        model_name = "BAAI/bge-m3"
        logger.info(f"Loading local embedding model: {model_name}")
        _embedding_model = SentenceTransformer(model_name)
        logger.info(f"Local embedding model loaded: {model_name}")
    except ImportError:
        logger.warning("sentence-transformers not installed, embedding unavailable")
        _embedding_model = None
    except Exception as exc:
        logger.error(f"Failed to load local embedding model: {exc}")
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
