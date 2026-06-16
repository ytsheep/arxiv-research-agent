"""Agent Orchestrator: API-facing facade over the LangGraph agent graph.

Routes simple tasks to LangGraphAgentRunner and compound tasks to
MultiAgentGraphRunner based on keyword complexity detection.
"""

import re
from collections.abc import Awaitable, Callable
from typing import Any

from app.agent.graph_runner import LangGraphAgentRunner
from app.agent.multi_agent_runner import MultiAgentGraphRunner
from app.agent.bootstrap import create_tool_registry
from app.schemas.chat import ChatResponse
from app.tools.trace_tool import Trace, TraceTool
from app.core.logging import logger


class AgentOrchestrator:
    """Routes between simple and compound task runners."""

    def __init__(self, use_react: bool | None = None):
        self.trace_tool = TraceTool()
        self.tool_registry = create_tool_registry()
        self.graph_runner = LangGraphAgentRunner(
            trace_tool=self.trace_tool,
            use_react=use_react,
        )
        self.multi_agent_runner = MultiAgentGraphRunner(
            trace_tool=self.trace_tool,
            tool_registry=self.tool_registry,
        )

    async def handle_chat(
        self,
        message: str,
        session_id: str,
        trace: Trace | None = None,
        progress_callback: Callable[[dict[str, Any]], Awaitable[None]] | None = None,
    ) -> ChatResponse:
        complexity = self._detect_complexity(message)
        if complexity == "compound":
            logger.info(f"Routing to multi-agent: {message[:80]}")
            return await self.multi_agent_runner.run_chat(
                message, session_id, trace=trace, progress_callback=progress_callback,
            )
        return await self.graph_runner.run_chat(
            message, session_id, trace=trace, progress_callback=progress_callback,
        )

    def create_trace(self, message: str) -> Trace:
        if self._detect_complexity(message) == "compound":
            return self.trace_tool.create(
                task_type="multi_agent_workflow",
                user_input=message,
                tags=["multi_agent", "compound"],
            )
        return self.trace_tool.create(
            task_type="chat",
            user_input=message,
            tags=["langgraph"],
        )

    async def get_state_history(self, trace_id: str):
        return await self.graph_runner.get_state_history(trace_id)

    async def close(self) -> None:
        await self.graph_runner.close()
        await self.multi_agent_runner.close()

    @staticmethod
    def _detect_complexity(message: str) -> str:
        """Detect compound vs simple tasks using keyword heuristics.

        Returns 'compound' if the message contains multiple action verbs
        joined by sequential connectors.
        """
        action_verbs = [
            "找", "搜", "检索", "对比", "比较", "收藏", "解析", "精读",
            "推荐", "总结", "综述", "评估", "选择", "挑",
        ]
        compound_connectors = [
            r"(并且|然后|之后|接着|再把|并把|并|再|最后)",
            r"(先.*再.*然后|首先.*然后.*最后|第一个.*第二个)",
        ]

        action_count = sum(1 for v in action_verbs if v in message)

        if action_count >= 3:
            return "compound"

        if action_count >= 2:
            # 2+ action verbs with connectors or comma/semicolon separators
            if re.search(r"[，,;；]", message):
                return "compound"
            for connector in compound_connectors:
                if re.search(connector, message):
                    return "compound"

        return "simple"
