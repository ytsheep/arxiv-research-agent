"""Project LangGraph checkpoint history into Trace UI records."""

from __future__ import annotations

from typing import Any

from app.tools.trace_tool import TraceTool


class TraceProjectionService:
    """Builds frontend trace details from LangGraph state history."""

    def __init__(self, history_provider, trace_tool: TraceTool):
        self.history_provider = history_provider
        self.trace_tool = trace_tool

    async def get_trace(self, trace_id: str) -> dict | None:
        old_trace = await self.trace_tool.get(trace_id)
        snapshots = await self._get_snapshots(trace_id)
        if not snapshots:
            return old_trace

        latest = snapshots[0].values if snapshots else {}
        steps = self._project_steps(snapshots)

        return {
            "trace_id": trace_id,
            "task_type": old_trace.get("task_type", "chat") if old_trace else "chat",
            "user_input": old_trace.get("user_input", latest.get("user_message", "")) if old_trace else latest.get("user_message", ""),
            "summary": old_trace.get("summary", "") if old_trace else "",
            "tags": old_trace.get("tags", ["langgraph"]) if old_trace else ["langgraph"],
            "status": old_trace.get("status", latest.get("status", "")) if old_trace else latest.get("status", ""),
            "started_at": old_trace.get("started_at", "") if old_trace else "",
            "ended_at": old_trace.get("ended_at", "") if old_trace else "",
            "duration_ms": old_trace.get("duration_ms", 0) if old_trace else 0,
            "error_message": old_trace.get("error_message", latest.get("error", "")) if old_trace else latest.get("error", ""),
            "steps": steps,
        }

    async def count_steps(self, trace_id: str) -> int:
        snapshots = await self._get_snapshots(trace_id)
        return len(self._project_steps(snapshots)) if snapshots else 0

    async def _get_snapshots(self, trace_id: str) -> list[Any]:
        try:
            return await self.history_provider(trace_id)
        except Exception:
            return []

    def _project_steps(self, snapshots: list[Any]) -> list[dict[str, Any]]:
        steps = []
        last_step_name = ""
        for snapshot in reversed(snapshots):
            values = snapshot.values or {}
            step_name = values.get("current_node", "")
            if not step_name or step_name == last_step_name:
                continue
            last_step_name = step_name
            agent_name, step_type = self._agent_info(step_name)
            steps.append({
                "step_name": step_name,
                "tool_name": values.get("selected_tool", "") or step_name,
                "reasoning_summary": values.get("reasoning_summary", ""),
                "input_summary": self._input_summary(values),
                "output_summary": self._output_summary(values),
                "status": values.get("status", "success"),
                "started_at": snapshot.created_at or "",
                "ended_at": snapshot.created_at or "",
                "duration_ms": 0,
                "error_message": values.get("error", ""),
                "agent_name": agent_name,
                "step_type": step_type,
            })
        return steps

    @staticmethod
    def _agent_info(node_name: str) -> tuple[str, str]:
        agent_map = {
            "supervisor_init": ("supervisor", "planning"),
            "supervisor_plan": ("supervisor", "planning"),
            "supervisor_dispatch": ("supervisor", "dispatching"),
            "executor_run": ("executor", "execution"),
            "reviewer_check": ("reviewer", "review"),
            "workflow_review": ("reviewer", "workflow_review"),
            "composer_build": ("reviewer", "composition"),
            "error_handler": ("supervisor", "error"),
        }
        return agent_map.get(node_name, ("", ""))

    def _input_summary(self, values: dict[str, Any]) -> str:
        parts = []
        if values.get("user_message"):
            parts.append(f"user_message={values['user_message'][:120]}")
        if values.get("normalized_query"):
            parts.append(f"query={values['normalized_query']}")
        if values.get("top_n"):
            parts.append(f"top_n={values['top_n']}")
        if values.get("candidate_k"):
            parts.append(f"candidate_k={values['candidate_k']}")
        if values.get("tool_arguments"):
            parts.append(f"arguments={str(values['tool_arguments'])[:200]}")
        return "; ".join(parts)

    def _output_summary(self, values: dict[str, Any]) -> str:
        if values.get("intent"):
            base = f"intent={values['intent']}"
        else:
            base = ""

        counts = []
        if values.get("candidate_papers") is not None:
            counts.append(f"candidates={len(values.get('candidate_papers', []))}")
        if values.get("reranked_papers") is not None:
            counts.append(f"reranked={len(values.get('reranked_papers', []))}")
        if values.get("papers") is not None:
            counts.append(f"papers={len(values.get('papers', []))}")
        if values.get("tool_observation"):
            obs = values["tool_observation"]
            counts.append(f"observation_success={obs.get('success')}")
            if obs.get("message"):
                counts.append(f"message={obs.get('message')[:160]}")
        if values.get("final_response"):
            counts.append(f"response_type={values['final_response'].get('type', '')}")
        # Multi-agent fields
        if values.get("task_plan"):
            counts.append(f"plan_tasks={len(values.get('task_plan', []))}")
        if values.get("current_task_id"):
            counts.append(f"current_task={values.get('current_task_id')}")
        if values.get("last_review_decision"):
            counts.append(f"review={values.get('last_review_decision')}")
        if values.get("task_outputs"):
            counts.append(f"task_outputs={list(values.get('task_outputs', {}).keys())}")

        return "; ".join([item for item in [base, *counts] if item])
