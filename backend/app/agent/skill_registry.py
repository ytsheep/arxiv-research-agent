"""Skill Registry: wraps stable multi-step workflows as callable tools (Skill-as-Tool).

Each skill is a pre-defined pipeline of tool calls. The ReAct Agent sees them as
high-level tools, avoiding the risk of the model improvising unsafe tool sequences.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Awaitable
from app.core.logging import logger


@dataclass
class SkillDefinition:
    name: str
    description: str
    schema: dict
    handler: Callable[..., Awaitable[dict]]
    allowed_intents: list[str]
    permission: str = "read_only"


class SkillRegistry:
    """Registry for Skills, exposed as high-level callable tools."""

    def __init__(self):
        self._skills: dict[str, SkillDefinition] = {}

    def register(self, skill: SkillDefinition) -> None:
        if skill.name in self._skills:
            raise ValueError(f"Skill already registered: {skill.name}")
        self._skills[skill.name] = skill
        logger.info(f"Skill registered: {skill.name}")

    def get(self, name: str) -> SkillDefinition:
        if name not in self._skills:
            raise ValueError(f"Unknown skill: {name}")
        return self._skills[name]

    def list_schemas(self, intent: str | None = None) -> list[dict]:
        skills = list(self._skills.values())
        if intent:
            skills = [
                s for s in skills
                if intent in s.allowed_intents or "*" in s.allowed_intents
            ]
        return [s.schema for s in skills]

    async def call(self, name: str, arguments: dict) -> dict:
        skill = self.get(name)
        try:
            return await skill.handler(**arguments)
        except Exception as e:
            logger.error(f"Skill '{name}' failed: {e}")
            return {"success": False, "error": str(e)}

    def __len__(self) -> int:
        return len(self._skills)

    def __contains__(self, name: str) -> bool:
        return name in self._skills
