"""Supervisor Dispatcher: finds ready tasks and resolves dependencies."""

from app.core.logging import logger


class SupervisorDispatcher:
    """Manages task dispatch based on dependency DAG."""

    def find_ready_tasks(self, task_plan: list[dict], completed: list[str], running: list[str], failed: list[str]) -> list[str]:
        """Return task_ids whose dependencies are all met and not yet processed."""
        ready = []
        for item in task_plan:
            tid = item.get("task_id", "")
            if tid in completed or tid in running or tid in failed:
                continue
            deps = item.get("depends_on", [])
            if isinstance(deps, list) and all(d in completed for d in deps):
                ready.append(tid)
        return ready

    def find_task_item(self, task_plan: list[dict], task_id: str) -> dict | None:
        for item in task_plan:
            if item.get("task_id") == task_id:
                return item
        return None

    def all_tasks_done(self, task_plan: list[dict], completed: list[str], failed: list[str]) -> bool:
        total_ids = {item.get("task_id", "") for item in task_plan}
        done = set(completed) | set(failed)
        return total_ids.issubset(done)

    def has_blocked_tasks(self, task_plan: list[dict], completed: list[str], running: list[str], failed: list[str]) -> bool:
        """Check for circular dependency: some pending tasks, but nothing is ready."""
        ready = self.find_ready_tasks(task_plan, completed, running, failed)
        all_processed = set(completed) | set(running) | set(failed)
        total = {item.get("task_id", "") for item in task_plan}
        pending = total - all_processed
        return len(pending) > 0 and len(ready) == 0
