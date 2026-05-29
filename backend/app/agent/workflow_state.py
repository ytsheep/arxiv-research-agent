"""WorkflowState: TypedDict for multi-agent compound task workflows.

Separate from PaperAgentState to keep the existing simple-task path
unaffected. Checkpointer persists this state on every node transition.
"""

from __future__ import annotations

from typing import Any, TypedDict


class TaskPlanItem(TypedDict, total=False):
    task_id: str
    task_type: str
    description: str
    depends_on: list[str]
    required_outputs: list[str]
    assigned_skill: str
    status: str  # pending | running | completed | failed | skipped
    retry_count: int


class WorkflowState(TypedDict, total=False):
    trace_id: str
    session_id: str
    workflow_id: str
    user_message: str
    complexity: str  # "simple" | "compound"

    task_plan: list[dict[str, Any]]  # list[TaskPlanItem]
    task_plan_raw: dict[str, Any]  # raw LLM plan output for diagnostics
    current_task_id: str
    task_outputs: dict[str, dict[str, Any]]  # task_id -> output

    pending_tasks: list[str]
    running_tasks: list[str]
    completed_tasks: list[str]
    failed_tasks: list[str]

    message_history: list[dict[str, Any]]

    last_review_decision: str  # continue | retry | replan | partial_final | finish
    retry_count: int
    replan_count: int
    max_retries: int
    max_replans: int

    user_preferences: dict[str, Any]
    long_term_memories: list[dict[str, Any]]
    last_papers: list[dict[str, Any]]

    selected_paper: dict[str, Any]
    final_response: dict[str, Any]
    status: str
    error: str

    current_node: str
    top_n: int
    candidate_k: int
