"""ReAct Agent: controlled Reasoning + Acting loop for paper research tasks.

The agent is NOT fully autonomous. It operates within strict bounds:
- Only tools registered in the ToolRegistry can be called
- Business rules are enforced (no full-text parsing during search, etc.)
- max_steps limits runaway loops
- Every step is traced for observability
"""

from __future__ import annotations
from typing import Any
from app.agent.tool_registry import ToolRegistry
from app.tools.llm_client import LLMClient, llm_client
from app.tools.trace_tool import TraceTool
from app.core.logging import logger

MAX_STEPS = 6


class AgentState:
    """Mutable state bag for a single ReAct run."""

    def __init__(self, user_message: str, session_id: str = ""):
        self.user_message = user_message
        self.session_id = session_id
        self.observations: list[dict] = []
        self.step_count = 0
        self.intent = "paper_search"

    def add_observation(self, obs: dict) -> None:
        self.observations.append(obs)

    def to_summary(self) -> str:
        """Produce a compact text summary of observations so far."""
        if not self.observations:
            return "No observations yet."
        lines = []
        for i, obs in enumerate(self.observations[-4:]):  # last 4 only
            status = "OK" if obs.get("success") else "FAIL"
            summary = str(obs.get("summary", obs.get("message", "")))[:150]
            lines.append(f"[{i + 1}] {status}: {summary}")
        return "\n".join(lines)


class ReactAgent:
    """Controlled ReAct Agent for arXiv paper research.

    Supports intents: paper_search, library_search, trace_search (read-only only in MVP).
    """

    def __init__(
        self,
        tool_registry: ToolRegistry | None = None,
        llm: LLMClient | None = None,
        trace_tool: TraceTool | None = None,
    ):
        self.tool_registry = tool_registry
        self.llm = llm or llm_client
        self.trace_tool = trace_tool or TraceTool()

    async def run(
        self,
        message: str,
        session_id: str = "",
        intent: str = "paper_search",
    ) -> dict:
        """Execute a ReAct loop for the given user message.

        Returns a dict suitable for ChatResponse construction."""
        trace = self.trace_tool.create(
            task_type="react_agent",
            user_input=message,
            tags=[intent, "react_agent"],
        )
        logger.info(f"[ReAct trace={trace.trace_id}] Starting agent for: {message[:80]}")

        state = AgentState(user_message=message, session_id=session_id)
        state.intent = intent

        # Get allowed tools for this intent
        tools = self._get_allowed_tools(intent)
        tool_schemas = [t.schema for t in tools]

        for step_idx in range(MAX_STEPS):
            state.step_count = step_idx + 1

            # ── Plan ───────────────────────────────────────────────
            plan_result = await self.llm.plan_with_tools(
                user_message=message,
                state_summary=state.to_summary(),
                tools=tool_schemas,
                usage_stage="legacy_react_planning",
            )

            await self.trace_tool.log_step(
                trace_id=trace.trace_id,
                step_name=f"react_step_{step_idx + 1}",
                tool_name=plan_result.get("action", "unknown"),
                input_summary=state.to_summary()[:500],
                output_summary=plan_result.get("reasoning_summary", "")[:500],
                status="success" if plan_result["success"] else "failed",
                error_message=plan_result.get("error", ""),
            )

            action = plan_result.get("action", "final_answer")
            reasoning = plan_result.get("reasoning_summary", "")

            # ── Terminal ───────────────────────────────────────────
            if action == "final_answer":
                await self.trace_tool.complete(
                    trace.trace_id,
                    status="success",
                    trace=trace,
                )
                return self._build_final_response(
                    trace_id=trace.trace_id,
                    message=reasoning or "Task completed.",
                    observations=state.observations,
                )

            # ── Validate ───────────────────────────────────────────
            if action not in self.tool_registry:
                err_msg = f"Unknown tool '{action}' — not in registry"
                state.add_observation({"success": False, "message": err_msg})
                continue

            # ── Execute ────────────────────────────────────────────
            arguments = plan_result.get("arguments", {})
            obs = await self.tool_registry.call(
                name=action,
                arguments=arguments,
                context={"intent": intent, "step": step_idx + 1},
            )

            await self.trace_tool.log_step(
                trace_id=trace.trace_id,
                step_name=action,
                tool_name=action,
                input_summary=str(arguments)[:500],
                output_summary=str(obs.get("message", obs.get("error", "")))[:500],
                status="success" if obs.get("success") else "failed",
                error_message=obs.get("error", obs.get("message", "")),
            )

            state.add_observation(obs)

            # ── Handle failure ─────────────────────────────────────
            if not obs.get("success"):
                # If a tool fails, give the model one more chance,
                # but do NOT loop on repeated failures
                continue

        # ── Exhausted max_steps ────────────────────────────────────
        await self.trace_tool.complete(
            trace.trace_id,
            status="failed",
            error_message=f"ReAct reached max_steps ({MAX_STEPS}) without final_answer",
            trace=trace,
        )
        return {
            "success": False,
            "type": "error",
            "trace_id": trace.trace_id,
            "message": "任务执行步骤过多，已停止。请缩小问题范围后重试。",
            "papers": [],
        }

    def _get_allowed_tools(self, intent: str) -> list:
        """Get tools allowed for the given intent."""
        return [
            t for t in self.tool_registry._tools.values()
            if intent in t.allowed_intents or "*" in t.allowed_intents
        ]

    def _build_final_response(
        self,
        trace_id: str,
        message: str,
        observations: list[dict],
    ) -> dict:
        """Build the final response from accumulated observations."""
        papers = []
        for obs in observations:
            if obs.get("papers"):
                papers.extend(obs["papers"])
            if obs.get("ranked_papers"):
                papers.extend(obs["ranked_papers"])

        # Deduplicate by arxiv_id
        seen = set()
        unique = []
        for p in papers:
            aid = p.get("arxiv_id", "")
            if aid and aid not in seen:
                seen.add(aid)
                unique.append(p)

        return {
            "success": True,
            "type": "paper_search_result",
            "trace_id": trace_id,
            "message": message,
            "papers": unique,
        }
