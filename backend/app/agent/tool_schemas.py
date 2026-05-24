"""Tool schemas: OpenAI function schemas for registered tools."""

from dataclasses import dataclass, field
from typing import Callable, Awaitable, Literal

ToolPermission = Literal[
    "read_only",
    "write_safe",
    "write_dangerous",
    "expensive",
    "external_send",
]


@dataclass
class ToolDefinition:
    name: str
    description: str
    schema: dict
    handler: Callable[..., Awaitable[dict]]
    allowed_intents: list[str]
    permission: ToolPermission
    requires_confirmation: bool = False


# ── OpenAI function schemas ──────────────────────────────────────────

ARXIV_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "arxiv_search",
        "description": "Search arXiv for papers matching a research topic query. Returns paper metadata (title, authors, abstract, categories, dates). Does NOT download PDFs or parse full text.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Research topic or keywords to search for, e.g. 'reinforcement learning agents'",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of candidate papers to return (default 20, max 50)",
                    "default": 20,
                },
                "categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "arXiv categories to filter by, e.g. ['cs.AI', 'cs.CL']",
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["relevance", "submittedDate", "lastUpdatedDate"],
                    "description": "Sort order for results",
                },
            },
            "required": ["query"],
        },
    },
}

PAPER_RERANK_SCHEMA = {
    "type": "function",
    "function": {
        "name": "paper_rerank",
        "description": "Rerank candidate papers by semantic similarity, keyword match, recency, and user preferences. Returns top N papers with scores.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The original user query for semantic matching",
                },
                "papers": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of candidate paper dicts from arxiv_search",
                },
                "top_n": {
                    "type": "integer",
                    "description": "Number of top papers to return (default 2)",
                    "default": 2,
                },
            },
            "required": ["query", "papers"],
        },
    },
}

PAPER_GENERATE_CARD_SUMMARY_SCHEMA = {
    "type": "function",
    "function": {
        "name": "paper_generate_card_summary",
        "description": "Generate a Chinese card summary for a paper based on its title and abstract. Uses LLM when available, falls back to regex extraction. Does NOT access full text.",
        "parameters": {
            "type": "object",
            "properties": {
                "paper": {
                    "type": "object",
                    "description": "Paper dict with title and abstract fields",
                },
                "query": {
                    "type": "string",
                    "description": "User's original research topic for relevance context",
                },
            },
            "required": ["paper"],
        },
    },
}

LIBRARY_SEARCH_PAPERS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "library_search_papers",
        "description": "Search the local paper library. Returns papers that have been collected/parsed, with status and file availability info.",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Keyword to search in paper titles and abstracts",
                },
                "status": {
                    "type": "string",
                    "description": "Filter by paper status: collected, parsed, deleted",
                },
                "page": {
                    "type": "integer",
                    "description": "Page number (default 1)",
                    "default": 1,
                },
                "page_size": {
                    "type": "integer",
                    "description": "Results per page (default 20)",
                    "default": 20,
                },
            },
        },
    },
}

TRACE_QUERY_SCHEMA = {
    "type": "function",
    "function": {
        "name": "trace_query",
        "description": "Query task execution traces. Search by keyword, task type, status, or tags. Returns trace summaries with step counts.",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Search keyword for user_input or summary",
                },
                "task_type": {
                    "type": "string",
                    "description": "Filter by task type: chat, paper_search, paper_collect, paper_parse, subscription_run, etc.",
                },
                "status": {
                    "type": "string",
                    "description": "Filter by status: running, success, failed",
                },
                "page": {
                    "type": "integer",
                    "description": "Page number (default 1)",
                    "default": 1,
                },
                "page_size": {
                    "type": "integer",
                    "description": "Results per page (default 20)",
                    "default": 20,
                },
            },
        },
    },
}
