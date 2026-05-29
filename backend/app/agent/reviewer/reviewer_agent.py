"""Reviewer Agent: validates task outputs and decides next action."""

from app.core.logging import logger
from .completion_checker import CompletionChecker


class ReviewerAgent:
    """Reviews task outputs and decides: continue, retry, replan, partial_final, finish."""

    def __init__(self):
        self.checker = CompletionChecker()

    async def review_task(
        self,
        task_type: str,
        task_output: dict,
        task_item: dict,
        retry_count: int = 0,
        max_retries: int = 2,
    ) -> dict:
        is_complete, missing = self.checker.check_task(task_type, task_output)
        task_id = task_item.get("task_id", "")

        if is_complete:
            return {
                "decision": "continue",
                "reason": f"Task {task_id} completed successfully",
                "missing_fields": [],
                "suggested_fix": "",
            }

        if not task_output.get("success", True):
            if retry_count < max_retries:
                return {
                    "decision": "retry",
                    "reason": f"Task {task_id} failed: {task_output.get('error', task_output.get('message', ''))}",
                    "missing_fields": missing,
                    "suggested_fix": f"Retry {task_type} with same inputs (attempt {retry_count + 1}/{max_retries})",
                }
            else:
                return {
                    "decision": "replan",
                    "reason": f"Task {task_id} failed after {max_retries} retries",
                    "missing_fields": missing,
                    "suggested_fix": "Consider alternative approach or skip this task",
                }

        if missing:
            if retry_count < max_retries:
                return {
                    "decision": "retry",
                    "reason": f"Task {task_id} missing outputs: {missing}",
                    "missing_fields": missing,
                    "suggested_fix": f"Ensure output contains: {missing} (attempt {retry_count + 1}/{max_retries})",
                }
            else:
                return {
                    "decision": "replan",
                    "reason": f"Task {task_id} cannot complete after {max_retries} retries: missing {missing}",
                    "missing_fields": missing,
                    "suggested_fix": "Skip this task and continue with available results",
                }

        logger.warning(f"[Reviewer] Unknown state for {task_id}: complete={is_complete}, output_keys={list(task_output.keys())}")
        return {
            "decision": "continue",
            "reason": "OK (default)",
            "missing_fields": [],
            "suggested_fix": "",
        }

    async def review_workflow(self, task_plan: list[dict], completed: list[str], failed: list[str]) -> dict:
        is_terminal, decision = self.checker.check_workflow_complete(task_plan, completed, failed)
        completed_count = len(completed)
        failed_count = len(failed)
        total = len(task_plan)

        return {
            "decision": decision,
            "reason": f"Workflow: {completed_count}/{total} completed, {failed_count} failed",
        }
