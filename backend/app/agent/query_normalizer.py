"""Query normalization: fix typos, standardize terms, rewrite query for arXiv search."""

from app.agent.intent_classifier import normalize_query, TYPO_MAP


def normalize_search_query(raw_query: str) -> str:
    """Normalize a search query for arXiv API."""
    query = raw_query.strip()
    query = normalize_query(query)
    return query


def normalize_topic(topic: str) -> str:
    """Normalize a topic string."""
    return normalize_query(topic)
