"""Shared state schema for the LangGraph paper agent."""

from __future__ import annotations

from typing import Any, TypedDict


class PaperAgentState(TypedDict, total=False):
    """Business state passed between LangGraph nodes.

    This state describes the task itself. Detailed step logs are projected from
    checkpoint history instead of being stored as per-step fields here.
    """

    trace_id: str
    session_id: str
    user_message: str
    intent: str
    intent_result: dict[str, Any]
    entities: dict[str, Any]

    query: str
    normalized_query: str
    candidate_k: int
    top_n: int

    candidate_papers: list[dict[str, Any]]
    reranked_papers: list[dict[str, Any]]
    selected_papers: list[dict[str, Any]]
    summaries: list[dict[str, Any]]
    papers: list[dict[str, Any]]

    messages: list[dict[str, Any]]
    conversation_summary: str
    last_papers: list[dict[str, Any]]
    referenced_paper: dict[str, Any]
    long_term_memories: list[dict[str, Any]]
    user_preferences: dict[str, Any]
    interest_query: str

    observations: list[dict[str, Any]]
    reasoning_summary: str
    selected_tool: str
    tool_arguments: dict[str, Any]
    tool_observation: dict[str, Any]

    original_query: str
    rewritten_query: str
    query_rewrite_source: str
    query_filters: dict[str, Any]
    selected_skill: str
    slots: dict[str, Any]
    needs_clarification: bool
    clarification_question: str

    report_markdown: str
    comparison: dict[str, Any]
    survey_markdown: str

    current_node: str
    status: str
    error: str
    step_count: int
    max_steps: int
    final_response: dict[str, Any]
