"""Shared orchestrator instance to ensure trace consistency."""

from app.agent.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()
