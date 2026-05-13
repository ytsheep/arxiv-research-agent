"""Embedding tool: compute text embeddings for semantic reranking.

Uses LLM embedding API when available (OpenAI text-embedding-3-small),
falls back to TF-IDF cosine similarity with pure Python.
"""

from __future__ import annotations
import math
import re
from collections import Counter
from app.core.logging import logger


def _tokenize(text: str) -> list[str]:
    """Basic tokenizer: lowercase, split on non-alphanumeric, filter short tokens."""
    text = text.lower()
    tokens = re.findall(r"[a-zA-Z0-9一-鿿]+", text)
    return [t for t in tokens if len(t) > 1]


def _build_tfidf_vectors(
    query: str,
    documents: list[str],
) -> tuple[list[float], list[list[float]]]:
    """Build TF-IDF vectors for query and documents. Pure Python implementation."""
    query_tokens = _tokenize(query)
    doc_tokens_list = [_tokenize(doc) for doc in documents]

    # Build vocabulary from all documents
    vocab: dict[str, int] = {}
    for tokens in [query_tokens] + doc_tokens_list:
        for token in tokens:
            if token not in vocab:
                vocab[token] = len(vocab)

    if not vocab:
        return [], [[] for _ in documents]

    n_docs = len(documents)
    idf: dict[str, float] = {}
    for term in vocab:
        doc_count = sum(1 for tokens in doc_tokens_list if term in tokens)
        idf[term] = math.log((n_docs + 1) / (doc_count + 1)) + 1.0

    def vectorize(tokens: list[str]) -> list[float]:
        tf = Counter(tokens)
        vec = [0.0] * len(vocab)
        for term, idx in vocab.items():
            vec[idx] = tf.get(term, 0) * idf.get(term, 1.0)
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    query_vec = vectorize(query_tokens)
    doc_vecs = [vectorize(tokens) for tokens in doc_tokens_list]

    return query_vec, doc_vecs


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class EmbeddingTool:
    """Compute text embeddings and similarity scores."""

    async def rank_by_similarity(
        self,
        query: str,
        papers: list[dict],
        top_n: int = 5,
    ) -> tuple[list[dict], str]:
        """Rank papers by semantic similarity to query.

        Uses LLM embeddings when available, TF-IDF fallback otherwise.
        Returns (ranked_papers, method_used).
        """
        if not papers:
            return [], "none"

        # Build document texts
        doc_texts = []
        for paper in papers:
            title = paper.get("title", "")
            abstract = paper.get("abstract", paper.get("summary", ""))
            doc_texts.append(f"{title}. {abstract}")

        try:
            from app.tools.llm_client import llm_client

            if llm_client.available:
                result = await self._llm_rerank(query, doc_texts, papers, top_n)
                if result.get("success"):
                    return result["papers"], "LLM"
                logger.warning(f"LLM rerank failed, falling back to TF-IDF: {result.get('error')}")
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"LLM rerank error, falling back to TF-IDF: {e}")

        return self._tfidf_rerank(query, doc_texts, papers, top_n), "TF-IDF"

    async def _llm_rerank(
        self,
        query: str,
        doc_texts: list[str],
        papers: list[dict],
        top_n: int,
    ) -> dict:
        """Rerank using LLM embedding API."""
        from app.tools.llm_client import llm_client

        all_texts = [query] + doc_texts
        embed_result = await llm_client.embed(all_texts)

        if not embed_result.get("success"):
            return {"success": False, "error": embed_result.get("error", "")}

        embeddings = embed_result["embeddings"]
        query_embedding = embeddings[0]
        doc_embeddings = embeddings[1:]

        scored = []
        for i, (paper, doc_emb) in enumerate(zip(papers, doc_embeddings)):
            score = cosine_similarity(query_embedding, doc_emb)
            paper_copy = dict(paper)
            paper_copy["_rerank_score"] = round(score, 4)
            scored.append(paper_copy)

        scored.sort(key=lambda p: p["_rerank_score"], reverse=True)
        return {"success": True, "papers": scored[:top_n]}

    def _tfidf_rerank(
        self,
        query: str,
        doc_texts: list[str],
        papers: list[dict],
        top_n: int,
    ) -> list[dict]:
        """Rerank using TF-IDF cosine similarity."""
        query_vec, doc_vecs = _build_tfidf_vectors(query, doc_texts)

        scored = []
        for i, (paper, doc_vec) in enumerate(zip(papers, doc_vecs)):
            score = cosine_similarity(query_vec, doc_vec)
            paper_copy = dict(paper)
            paper_copy["_rerank_score"] = round(score, 4)
            scored.append(paper_copy)

        scored.sort(key=lambda p: p["_rerank_score"], reverse=True)
        return scored[:top_n]
