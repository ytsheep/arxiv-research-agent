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

LIBRARY_GET_PAPER_SCHEMA = {
    "type": "function",
    "function": {
        "name": "library_get_paper",
        "description": "Get a single paper from the local library by arXiv ID. Returns full metadata, file paths, and tags.",
        "parameters": {
            "type": "object",
            "properties": {
                "arxiv_id": {
                    "type": "string",
                    "description": "The arXiv paper ID, e.g. '2604.09537v1'",
                },
            },
            "required": ["arxiv_id"],
        },
    },
}

LIBRARY_GET_REPORT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "library_get_report",
        "description": "Get the Chinese deep reading report (report.md) for a paper from the local library.",
        "parameters": {
            "type": "object",
            "properties": {
                "arxiv_id": {
                    "type": "string",
                    "description": "The arXiv paper ID, e.g. '2604.09537v1'",
                },
            },
            "required": ["arxiv_id"],
        },
    },
}

PAPER_COLLECT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "paper_collect",
        "description": "Download a paper PDF from arXiv and save it to the local library with metadata. Does NOT parse full text or generate reports.",
        "parameters": {
            "type": "object",
            "properties": {
                "paper": {
                    "type": "object",
                    "description": "Paper dict with arxiv_id, title, pdf_url, authors, abstract, categories, published_date",
                },
            },
            "required": ["paper"],
        },
    },
}

PAPER_PARSE_FULL_TEXT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "paper_parse_full_text",
        "description": "Parse the full text of a PDF paper into structured sections and save as parsed.md. Requires the paper to already be collected (PDF downloaded). This is an expensive operation.",
        "parameters": {
            "type": "object",
            "properties": {
                "arxiv_id": {
                    "type": "string",
                    "description": "The arXiv paper ID to parse",
                },
            },
            "required": ["arxiv_id"],
        },
    },
}

PAPER_GENERATE_DEEP_REPORT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "paper_generate_deep_report",
        "description": "Generate a comprehensive Chinese deep reading report for a paper using LLM. Requires parsed.md to exist. This is an expensive operation.",
        "parameters": {
            "type": "object",
            "properties": {
                "arxiv_id": {
                    "type": "string",
                    "description": "The arXiv paper ID to generate a report for",
                },
            },
            "required": ["arxiv_id"],
        },
    },
}

SEMANTIC_MEMORY_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "semantic_memory_search",
        "description": "Search long-term semantic memory for papers, search history, reports, and preference summaries related to a query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for semantic retrieval",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of top results to return (default 5)",
                    "default": 5,
                },
                "source_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by source types: search_history, paper, report, preference_summary",
                },
            },
            "required": ["query"],
        },
    },
}

USER_PREFERENCE_GET_SCHEMA = {
    "type": "function",
    "function": {
        "name": "user_preference_get",
        "description": "Read current user research preferences: preferred topics, categories, topic interest weights, and defaults.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}

USER_PREFERENCE_UPDATE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "user_preference_update",
        "description": "Update user research preferences. Use action='set' to replace a value, 'append' to add to a list, 'remove' to remove from a list.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Preference key: preferred_topics, preferred_categories, summary_language, default_candidate_k, default_top_n, etc.",
                },
                "value": {
                    "type": "string",
                    "description": "New value for the preference key",
                },
                "action": {
                    "type": "string",
                    "enum": ["set", "append", "remove"],
                    "description": "How to apply the value: 'set' replaces, 'append' adds to existing, 'remove' deletes from existing",
                },
            },
            "required": ["key", "value"],
        },
    },
}

TRACE_GET_SCHEMA = {
    "type": "function",
    "function": {
        "name": "trace_get",
        "description": "Get the full detail of a single task trace by trace_id, including all steps with timing, input/output summaries, and errors.",
        "parameters": {
            "type": "object",
            "properties": {
                "trace_id": {
                    "type": "string",
                    "description": "The trace ID to fetch details for",
                },
            },
            "required": ["trace_id"],
        },
    },
}
