"""Bootstrap the Tool Registry with real tool instances."""

from app.agent.tool_registry import ToolRegistry
from app.agent.tool_schemas import (
    ToolDefinition,
    ARXIV_SEARCH_SCHEMA,
    PAPER_RERANK_SCHEMA,
    PAPER_GENERATE_CARD_SUMMARY_SCHEMA,
    LIBRARY_SEARCH_PAPERS_SCHEMA,
    TRACE_QUERY_SCHEMA,
)
from app.tools.arxiv_tool import ArxivTool
from app.tools.rerank_tool import RerankTool
from app.tools.report_tool import ReportTool
from app.tools.library_tool import LibraryTool
from app.tools.trace_tool import TraceTool


def create_tool_registry() -> ToolRegistry:
    """Create and populate a ToolRegistry with all available tools."""
    registry = ToolRegistry()

    arxiv_tool = ArxivTool()
    rerank_tool = RerankTool()
    report_tool = ReportTool()
    library_tool = LibraryTool()
    trace_tool = TraceTool()

    # ── Read-only tools (Phase 1) ──────────────────────────────────

    registry.register(ToolDefinition(
        name="arxiv_search",
        description="Search arXiv for papers matching a research topic query",
        schema=ARXIV_SEARCH_SCHEMA,
        handler=arxiv_tool.search,
        allowed_intents=["paper_search", "subscription_run", "library_search", "*"],
        permission="read_only",
    ))

    registry.register(ToolDefinition(
        name="paper_rerank",
        description="Rerank candidate papers by semantic similarity, keyword, recency, and user preferences",
        schema=PAPER_RERANK_SCHEMA,
        handler=rerank_tool.rerank,
        allowed_intents=["paper_search", "subscription_run", "*"],
        permission="read_only",
    ))

    registry.register(ToolDefinition(
        name="paper_generate_card_summary",
        description="Generate a Chinese card summary for a paper based on title and abstract only",
        schema=PAPER_GENERATE_CARD_SUMMARY_SCHEMA,
        handler=report_tool.generate_card_summary,
        allowed_intents=["paper_search", "subscription_run", "*"],
        permission="read_only",
    ))

    registry.register(ToolDefinition(
        name="library_search_papers",
        description="Search the local paper library by keyword, status, or pagination",
        schema=LIBRARY_SEARCH_PAPERS_SCHEMA,
        handler=library_tool.search_papers,
        allowed_intents=["library_search", "trace_search", "*"],
        permission="read_only",
    ))

    registry.register(ToolDefinition(
        name="trace_query",
        description="Query task execution traces by keyword, task type, status, or pagination",
        schema=TRACE_QUERY_SCHEMA,
        handler=trace_tool.query,
        allowed_intents=["trace_search", "*"],
        permission="read_only",
    ))

    return registry
