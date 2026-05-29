"""Agent Orchestrator: API-facing facade over the LangGraph agent graph."""

from app.agent.graph_runner import LangGraphAgentRunner
from app.schemas.chat import ChatResponse
from app.tools.trace_tool import TraceTool


class AgentOrchestrator:
    """Keeps the existing service entry point while delegating flow control to LangGraph."""

    def __init__(self, use_react: bool | None = None):
        self.trace_tool = TraceTool()
        self.graph_runner = LangGraphAgentRunner(
            trace_tool=self.trace_tool,
            use_react=use_react,
        )

    async def handle_chat(self, message: str, session_id: str) -> ChatResponse:
        return await self.graph_runner.run_chat(message, session_id)

    async def get_state_history(self, trace_id: str):
        return await self.graph_runner.get_state_history(trace_id)

    async def close(self) -> None:
        await self.graph_runner.close()
