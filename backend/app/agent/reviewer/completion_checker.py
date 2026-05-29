"""Completion Checker: deterministic validation of task outputs."""

from app.agent.executor.execution_map import REQUIRED_OUTPUTS_MAP


class CompletionChecker:
    """Checks task outputs against required_outputs deterministically."""

    @staticmethod
    def check_task(task_type: str, task_output: dict) -> tuple[bool, list[str]]:
        """Returns (is_complete, missing_fields)."""
        required = REQUIRED_OUTPUTS_MAP.get(task_type, [])
        missing = []
        for field in required:
            value = task_output.get(field)
            if value is None:
                missing.append(field)
            elif isinstance(value, list) and len(value) == 0:
                missing.append(field)
            elif isinstance(value, str) and len(value.strip()) == 0:
                missing.append(field)
            elif isinstance(value, dict) and len(value) == 0:
                missing.append(field)
        return len(missing) == 0, missing

    @staticmethod
    def check_workflow_complete(
        task_plan: list[dict],
        completed_tasks: list[str],
        failed_tasks: list[str],
    ) -> tuple[bool, str]:
        """Returns (is_terminal, decision).

        decision is one of: "continue", "finish", "partial_final"
        """
        total = len(task_plan)
        completed = len(completed_tasks)
        failed = len(failed_tasks)

        # "final_summary" tasks are optional for completion
        non_final = [t for t in task_plan if t.get("task_type") != "final_summary"]
        non_final_ids = {t.get("task_id", "") for t in non_final}
        non_final_done = non_final_ids.issubset(set(completed_tasks) | set(failed_tasks))

        if not non_final_done:
            if failed > 0:
                return True, "partial_final"
            return False, "continue"

        if completed >= total - len(failed_tasks):
            if failed > 0:
                return True, "partial_final"
            return True, "finish"

        return False, "continue"
