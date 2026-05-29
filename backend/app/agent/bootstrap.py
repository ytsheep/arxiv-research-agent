"""Bootstrap the Tool Registry with real tool instances."""

import os
import json

from app.agent.tool_registry import ToolRegistry
from app.agent.tool_schemas import (
    ToolDefinition,
    ARXIV_SEARCH_SCHEMA,
    PAPER_RERANK_SCHEMA,
    PAPER_GENERATE_CARD_SUMMARY_SCHEMA,
    LIBRARY_SEARCH_PAPERS_SCHEMA,
    LIBRARY_GET_PAPER_SCHEMA,
    LIBRARY_GET_REPORT_SCHEMA,
    PAPER_COLLECT_SCHEMA,
    PAPER_PARSE_FULL_TEXT_SCHEMA,
    PAPER_GENERATE_DEEP_REPORT_SCHEMA,
    SEMANTIC_MEMORY_SEARCH_SCHEMA,
    USER_PREFERENCE_GET_SCHEMA,
    USER_PREFERENCE_UPDATE_SCHEMA,
    TRACE_QUERY_SCHEMA,
    TRACE_GET_SCHEMA,
)
from app.tools.arxiv_tool import ArxivTool
from app.tools.rerank_tool import RerankTool
from app.tools.report_tool import ReportTool
from app.tools.library_tool import LibraryTool
from app.tools.trace_tool import TraceTool
from app.tools.pdf_tool import PdfTool
from app.services.memory_service import SemanticMemoryService
from app.storage.file_manager import FileManager

from app.agent.skills.paper_search_card_skill import (
    PAPER_SEARCH_CARD_SKILL_SCHEMA,
    paper_search_card_skill,
)
from app.agent.skills.trace_diagnosis_skill import (
    TRACE_DIAGNOSIS_SKILL_SCHEMA,
    trace_diagnosis_skill,
)
from app.agent.skills.paper_deep_read_skill import (
    PAPER_DEEP_READ_SKILL_SCHEMA,
    paper_deep_read_skill,
)
from app.agent.skills.paper_compare_skill import (
    PAPER_COMPARE_SKILL_SCHEMA,
    paper_compare_skill,
)
from app.agent.skills.literature_survey_skill import (
    LITERATURE_SURVEY_SKILL_SCHEMA,
    literature_survey_skill,
)
from app.agent.skills.interest_recommendation_skill import (
    INTEREST_RECOMMENDATION_SKILL_SCHEMA,
    interest_recommendation_skill,
)
from app.agent.skills.memory_profile_skill import (
    MEMORY_PROFILE_SKILL_SCHEMA,
    memory_profile_skill,
)


def create_tool_registry() -> ToolRegistry:
    """Create and populate a ToolRegistry with all available tools."""
    registry = ToolRegistry()

    arxiv_tool = ArxivTool()
    rerank_tool = RerankTool()
    report_tool = ReportTool()
    library_tool = LibraryTool()
    trace_tool = TraceTool()
    pdf_tool = PdfTool()
    semantic_memory = SemanticMemoryService()
    file_manager = FileManager()

    # ── Inline tool handlers ─────────────────────────────────────────

    async def _paper_collect_handler(paper: dict) -> dict:
        arxiv_id = paper.get("arxiv_id", "")
        if not arxiv_id:
            return {"success": False, "error": "Missing arxiv_id"}
        pdf_result = await pdf_tool.download_pdf(
            arxiv_id=arxiv_id,
            pdf_url=paper.get("pdf_url", f"https://arxiv.org/pdf/{arxiv_id}"),
        )
        if not pdf_result.get("success"):
            return {"success": False, "error": pdf_result.get("error", "PDF_DOWNLOAD_FAILED")}
        return await library_tool.add_paper(
            paper=paper,
            files={"pdf_path": pdf_result["pdf_path"]},
            source="agent_collect",
            status="collected",
        )

    async def _paper_parse_full_text_handler(arxiv_id: str) -> dict:
        lib_result = await library_tool.get_paper(arxiv_id)
        pdf_path = ""
        if lib_result.get("success") and lib_result.get("files"):
            pdf_path = lib_result["files"].get("pdf_path", "")
        if not pdf_path:
            paper_dir = file_manager.get_paper_dir(arxiv_id)
            pdf_path = os.path.join(paper_dir, "paper.pdf")
        if not os.path.exists(pdf_path):
            return {"success": False, "error": "PDF_NOT_FOUND", "message": "PDF 文件不存在，请先收藏论文"}
        parse_result = await pdf_tool.parse_full_text(arxiv_id=arxiv_id, pdf_path=pdf_path)
        if parse_result.get("success"):
            await library_tool.update_after_parse(arxiv_id=arxiv_id, parsed_path=parse_result.get("parsed_path", ""))
        return parse_result

    async def _paper_generate_deep_report_handler(arxiv_id: str) -> dict:
        paper_dir = file_manager.get_paper_dir(arxiv_id)
        parsed_path = os.path.join(paper_dir, "parsed.md")
        if not os.path.exists(parsed_path):
            return {"success": False, "error": "PARSED_NOT_FOUND", "message": "parsed.md 不存在，请先解析全文"}
        with open(parsed_path, "r", encoding="utf-8") as f:
            parsed_md = f.read()
        metadata_path = os.path.join(paper_dir, "metadata.json")
        metadata = {}
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        result = await report_tool.generate_deep_report(
            arxiv_id=arxiv_id,
            parsed_markdown=parsed_md,
            metadata=metadata,
        )
        if result.get("success"):
            await library_tool.update_after_parse(arxiv_id=arxiv_id, report_path=result.get("report_path", ""))
        return result

    async def _semantic_memory_search_handler(
        query: str,
        top_k: int = 5,
        source_types: list | None = None,
    ) -> dict:
        results = await semantic_memory.retrieve(
            query=query,
            top_k=top_k,
            source_types=source_types,
        )
        return {"success": True, "results": results, "total": len(results)}

    async def _user_preference_get_handler() -> dict:
        prefs = await semantic_memory.load_user_preferences()
        return {"success": True, "preferences": prefs}

    async def _user_preference_update_handler(
        key: str,
        value: str,
        action: str = "set",
    ) -> dict:
        from app.agent.skills.memory_profile_skill import _update_preference
        summary = await _update_preference(key, value, action)
        return {"success": True, "key": key, "changes_summary": summary}

    async def _trace_get_handler(trace_id: str) -> dict:
        return await trace_tool.get(trace_id)

    # ── Read-only tools ──────────────────────────────────────────────

    registry.register(ToolDefinition(
        name="paper_search_card_skill",
        description="High-level Skill for safe paper search, rerank, and card generation",
        schema=PAPER_SEARCH_CARD_SKILL_SCHEMA,
        handler=paper_search_card_skill,
        allowed_intents=["paper_search", "subscription_run", "interest_recommendation", "literature_survey", "*"],
        permission="read_only",
    ))

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
        allowed_intents=["library_search", "trace_search", "paper_compare", "paper_deep_read", "*"],
        permission="read_only",
    ))

    registry.register(ToolDefinition(
        name="library_get_paper",
        description="Get a single paper from the local library by arXiv ID with full metadata and file info",
        schema=LIBRARY_GET_PAPER_SCHEMA,
        handler=library_tool.get_paper,
        allowed_intents=["paper_deep_read", "paper_compare", "library_search", "trace_diagnosis", "*"],
        permission="read_only",
    ))

    registry.register(ToolDefinition(
        name="library_get_report",
        description="Get the Chinese deep reading report for a paper from the local library",
        schema=LIBRARY_GET_REPORT_SCHEMA,
        handler=library_tool.get_report,
        allowed_intents=["paper_deep_read", "paper_compare", "report_view", "trace_diagnosis", "*"],
        permission="read_only",
    ))

    registry.register(ToolDefinition(
        name="semantic_memory_search",
        description="Search long-term semantic memory for papers, search history, and reports related to a query",
        schema=SEMANTIC_MEMORY_SEARCH_SCHEMA,
        handler=_semantic_memory_search_handler,
        allowed_intents=["paper_search", "interest_recommendation", "literature_survey", "paper_compare", "*"],
        permission="read_only",
    ))

    registry.register(ToolDefinition(
        name="user_preference_get",
        description="Read current user research preferences: topics, categories, interest weights",
        schema=USER_PREFERENCE_GET_SCHEMA,
        handler=_user_preference_get_handler,
        allowed_intents=["interest_recommendation", "memory_profile", "paper_search", "*"],
        permission="read_only",
    ))

    registry.register(ToolDefinition(
        name="trace_query",
        description="Query task execution traces by keyword, task type, status, or pagination",
        schema=TRACE_QUERY_SCHEMA,
        handler=trace_tool.query,
        allowed_intents=["trace_search", "trace_diagnosis", "*"],
        permission="read_only",
    ))

    registry.register(ToolDefinition(
        name="trace_get",
        description="Get full detail of a single task trace by trace_id, including all steps",
        schema=TRACE_GET_SCHEMA,
        handler=_trace_get_handler,
        allowed_intents=["trace_diagnosis", "trace_search", "*"],
        permission="read_only",
    ))

    # ── Write-safe tools ─────────────────────────────────────────────

    registry.register(ToolDefinition(
        name="paper_collect",
        description="Download a paper PDF from arXiv and save to local library with metadata",
        schema=PAPER_COLLECT_SCHEMA,
        handler=_paper_collect_handler,
        allowed_intents=["paper_collect", "paper_deep_read", "subscription_run", "*"],
        permission="write_safe",
    ))

    registry.register(ToolDefinition(
        name="user_preference_update",
        description="Update user research preferences. Use action='set' to replace, 'append' to add, 'remove' to delete.",
        schema=USER_PREFERENCE_UPDATE_SCHEMA,
        handler=_user_preference_update_handler,
        allowed_intents=["memory_profile", "*"],
        permission="write_safe",
    ))

    # ── Expensive tools ──────────────────────────────────────────────

    registry.register(ToolDefinition(
        name="paper_parse_full_text",
        description="Parse full text of a PDF paper into structured sections. Requires paper to be collected first.",
        schema=PAPER_PARSE_FULL_TEXT_SCHEMA,
        handler=_paper_parse_full_text_handler,
        allowed_intents=["paper_parse", "paper_deep_read", "subscription_run"],
        permission="expensive",
    ))

    registry.register(ToolDefinition(
        name="paper_generate_deep_report",
        description="Generate a comprehensive Chinese deep reading report for a paper using LLM. Requires parsed.md to exist.",
        schema=PAPER_GENERATE_DEEP_REPORT_SCHEMA,
        handler=_paper_generate_deep_report_handler,
        allowed_intents=["paper_parse", "paper_deep_read", "subscription_run"],
        permission="expensive",
    ))

    # ── Skill-level registrations ────────────────────────────────────

    registry.register(ToolDefinition(
        name="trace_diagnosis_skill",
        description="Query task execution traces and diagnose failures with fix suggestions",
        schema=TRACE_DIAGNOSIS_SKILL_SCHEMA,
        handler=trace_diagnosis_skill,
        allowed_intents=["trace_diagnosis", "trace_search", "*"],
        permission="read_only",
    ))

    registry.register(ToolDefinition(
        name="paper_deep_read_skill",
        description="Deep-read a paper: resolve reference, collect PDF if needed, parse full text, and generate a Chinese deep reading report",
        schema=PAPER_DEEP_READ_SKILL_SCHEMA,
        handler=paper_deep_read_skill,
        allowed_intents=["paper_deep_read", "paper_parse", "*"],
        permission="expensive",
    ))

    registry.register(ToolDefinition(
        name="paper_compare_skill",
        description="Compare multiple papers across problem, method, experiment, result, limitation, and value",
        schema=PAPER_COMPARE_SKILL_SCHEMA,
        handler=paper_compare_skill,
        allowed_intents=["paper_compare", "*"],
        permission="read_only",
    ))

    registry.register(ToolDefinition(
        name="literature_survey_skill",
        description="Search papers on a topic, summarize, and produce a small literature survey",
        schema=LITERATURE_SURVEY_SKILL_SCHEMA,
        handler=literature_survey_skill,
        allowed_intents=["literature_survey", "paper_search", "*"],
        permission="read_only",
    ))

    registry.register(ToolDefinition(
        name="interest_recommendation_skill",
        description="Recommend papers based on user's long-term research interests and semantic memory",
        schema=INTEREST_RECOMMENDATION_SKILL_SCHEMA,
        handler=interest_recommendation_skill,
        allowed_intents=["paper_search", "interest_recommendation", "*"],
        permission="read_only",
    ))

    registry.register(ToolDefinition(
        name="memory_profile_skill",
        description="Read or update user research preferences. Use action='read' to view, action='update' to modify.",
        schema=MEMORY_PROFILE_SKILL_SCHEMA,
        handler=memory_profile_skill,
        allowed_intents=["memory_profile", "*"],
        permission="write_safe",
    ))

    return registry
