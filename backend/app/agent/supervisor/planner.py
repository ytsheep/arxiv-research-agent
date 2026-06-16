"""Supervisor Planner: builds task plans from user messages."""

from app.tools.llm_client import llm_client
from app.core.logging import logger
from .prompts import PLANNER_SYSTEM_PROMPT, PLANNER_USER_TEMPLATE, build_rule_plan


class SupervisorPlanner:
    """Builds a structured task_plan from a compound user request."""

    async def plan(
        self,
        user_message: str,
        user_preferences: dict | None = None,
        long_term_memories: list[dict] | None = None,
    ) -> dict:
        """Returns {"success": bool, "task_plan": list[dict], "reason": str}."""
        if llm_client.available:
            result = await self._llm_plan(user_message, user_preferences)
            if result.get("success") and result.get("task_plan"):
                result["task_plan"] = self._normalize_task_plan(result["task_plan"])
                if result["task_plan"]:
                    return result
            logger.warning("LLM planning failed or returned empty, falling back to rules")

        return self._rule_plan(user_message)

    async def _llm_plan(self, user_message: str, user_preferences: dict | None = None) -> dict:
        prefs = user_preferences or {}
        prefs_text = ""
        if prefs.get("preferred_topics"):
            prefs_text = f"\nUser preferred topics: {prefs.get('preferred_topics', [])}"
        if prefs.get("preferred_categories"):
            prefs_text += f"\nUser preferred categories: {prefs.get('preferred_categories', [])}"

        prompt = PLANNER_USER_TEMPLATE.format(user_message=user_message + prefs_text)

        try:
            result = await llm_client.chat_json(
                messages=[
                    {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=2048,
                usage_stage="supervisor_planning",
            )
            if result.get("success") and result.get("data"):
                data = result["data"]
                task_plan = data.get("task_plan", [])
                if isinstance(task_plan, list) and len(task_plan) > 0:
                    # Validate task plan structure
                    valid = True
                    for item in task_plan:
                        if not isinstance(item, dict) or "task_id" not in item or "task_type" not in item:
                            valid = False
                            break
                    if valid:
                        return {
                            "success": True,
                            "task_plan": task_plan,
                            "reason": data.get("reason", "LLM-generated plan"),
                            "raw_llm_output": data,
                        }
        except Exception as e:
            logger.warning(f"LLM planning error: {e}")

        return {"success": False, "task_plan": [], "reason": "LLM planning failed"}

    def _rule_plan(self, user_message: str) -> dict:
        plan = build_rule_plan(user_message)
        if plan:
            plan["success"] = True
            return plan
        return {
            "success": False,
            "task_plan": [],
            "reason": "No applicable rule-based plan detected",
        }

    @staticmethod
    def _normalize_task_plan(task_plan: list[dict]) -> list[dict]:
        """Normalize LLM output references such as task_1.papers to task_1."""
        task_ids = {
            item.get("task_id", "")
            for item in task_plan
            if isinstance(item, dict) and item.get("task_id")
        }
        normalized = []
        for item in task_plan:
            if not isinstance(item, dict) or not item.get("task_id") or not item.get("task_type"):
                continue
            clean = dict(item)
            dependencies = []
            for dependency in clean.get("depends_on", []) or []:
                task_id = str(dependency).split(".", 1)[0]
                if task_id in task_ids and task_id != clean["task_id"] and task_id not in dependencies:
                    dependencies.append(task_id)
            clean["depends_on"] = dependencies
            normalized.append(clean)
        return normalized
