"""Executor Agent: runs exactly ONE task deterministically. No free-form ReAct."""

import asyncio

from app.agent.tool_registry import ToolRegistry
from app.agent.workflow_state import WorkflowState
from app.core.logging import logger
from .execution_map import EXECUTION_MAP
from .input_resolver import InputResolver


class ExecutorAgent:
    """Executes a single assigned task by deterministic Skill/Tool routing."""

    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry
        self.resolver = InputResolver()

    async def execute(
        self,
        task_item: dict,
        task_outputs: dict[str, dict],
        user_message: str,
        user_preferences: dict,
        default_top_n: int = 2,
        default_candidate_k: int = 20,
        timeout_seconds: int = 120,
    ) -> dict:
        task_type = task_item.get("task_type", "")
        task_id = task_item.get("task_id", "")
        logger.info(f"[Executor] Executing {task_id} ({task_type})")

        if task_type == "final_summary":
            return {"success": True, "final_summary": True}

        if task_type not in EXECUTION_MAP:
            return {"success": False, "error": f"Unknown task_type: {task_type}"}

        skill_name, arg_mapping = EXECUTION_MAP[task_type]
        resolved_args = self.resolver.resolve(
            arg_mapping, task_outputs, user_message, user_preferences,
            default_top_n, default_candidate_k,
        )

        logger.debug(f"[Executor] {task_id}: skill={skill_name}, args_keys={list(resolved_args.keys())}")

        try:
            result = await asyncio.wait_for(
                self.tool_registry.call(
                    name=skill_name,
                    arguments=resolved_args,
                    context={"intent": task_type, "multi_agent": True},
                ),
                timeout=timeout_seconds,
            )
            logger.info(f"[Executor] {task_id} completed: success={result.get('success')}")
            return result
        except asyncio.TimeoutError:
            logger.error(f"[Executor] {task_id} timeout after {timeout_seconds}s")
            return {"success": False, "error": f"Task execution timed out after {timeout_seconds}s", "task_id": task_id}
        except Exception as e:
            logger.error(f"[Executor] {task_id} error: {e}")
            return {"success": False, "error": str(e), "task_id": task_id}
