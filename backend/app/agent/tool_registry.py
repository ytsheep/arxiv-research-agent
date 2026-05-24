"""Tool Registry: registers, validates, and executes tools with permission checks."""

from __future__ import annotations
import json
from typing import Any
from app.agent.tool_schemas import ToolDefinition, ToolPermission
from app.core.logging import logger

# Business rules for tool access control
BUSINESS_RULES = {
    "paper_search": {
        "deny_tools": {"pdf_parse_full_text", "paper_generate_deep_report"},
        "reason": "Search phase must not trigger full-text parsing",
    },
    "paper_collect": {
        "deny_tools": {"pdf_parse_full_text", "paper_generate_deep_report"},
        "reason": "Collect only downloads PDF, parsing is a separate action",
    },
}


class ToolRegistry:
    """Central registry for all callable tools. Handles registration, schema listing,
    permission validation, business rule checks, and unified execution."""

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool
        logger.info(f"Tool registered: {tool.name} (permission={tool.permission})")

    def get(self, name: str) -> ToolDefinition:
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")
        return self._tools[name]

    def list_tools(self, intent: str | None = None) -> list[ToolDefinition]:
        """List all tools, optionally filtered by allowed intent."""
        tools = list(self._tools.values())
        if intent:
            tools = [
                t for t in tools
                if intent in t.allowed_intents or "*" in t.allowed_intents
            ]
        return tools

    def list_schemas(self, intent: str | None = None) -> list[dict]:
        """List OpenAI function schemas for tools, optionally filtered by intent."""
        return [t.schema for t in self.list_tools(intent)]

    def _validate_permission(
        self,
        tool: ToolDefinition,
        context: dict | None = None,
    ) -> tuple[bool, str]:
        """Check if the tool's permission level is allowed in the current context."""
        context = context or {}
        intent = context.get("intent", "*")

        # Check deny rules for the intent
        rules = BUSINESS_RULES.get(intent, {})
        deny_tools = rules.get("deny_tools", set())
        if tool.name in deny_tools:
            reason = rules.get("reason", "Tool not allowed for this intent")
            return False, reason

        return True, ""

    async def call(
        self,
        name: str,
        arguments: dict,
        context: dict | None = None,
    ) -> dict:
        """Validate and execute a tool call. Returns standard observation dict."""
        context = context or {}

        try:
            tool = self.get(name)
        except ValueError as e:
            return {
                "success": False,
                "error_code": "UNKNOWN_TOOL",
                "message": str(e),
                "detail": f"Tool '{name}' is not registered",
            }

        # Permission check
        allowed, reason = self._validate_permission(tool, context)
        if not allowed:
            return {
                "success": False,
                "error_code": "TOOL_NOT_ALLOWED",
                "message": f"Tool '{name}' is not allowed in this context",
                "detail": reason,
            }

        # Execute
        try:
            result = await tool.handler(**arguments)
            return result
        except TypeError as e:
            return {
                "success": False,
                "error_code": "INVALID_ARGUMENTS",
                "message": f"Invalid arguments for tool '{name}'",
                "detail": str(e),
            }
        except Exception as e:
            logger.error(f"Tool '{name}' execution failed: {e}")
            return {
                "success": False,
                "error_code": "TOOL_EXECUTION_FAILED",
                "message": f"Tool '{name}' execution failed",
                "detail": str(e),
            }

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools
