"""Memory Profile Skill: read and update user research preferences."""

import json
from datetime import datetime

from sqlalchemy import select
from app.db.database import async_session
from app.models.settings import UserPreference
from app.tools.trace_tool import TraceTool
from app.services.memory_service import SemanticMemoryService
from app.core.logging import logger

MEMORY_PROFILE_SKILL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "memory_profile_skill",
        "description": "Read or update user research preferences. Use action='read' to view current preferences, action='update' to modify them.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["read", "update"],
                    "description": "'read' to view preferences, 'update' to modify",
                },
                "key": {
                    "type": "string",
                    "description": "Preference key to update: preferred_topics, preferred_categories, etc.",
                },
                "value": {
                    "type": "string",
                    "description": "New value for the preference key",
                },
                "update_action": {
                    "type": "string",
                    "enum": ["set", "append", "remove"],
                    "description": "How to apply: 'set' replaces, 'append' adds, 'remove' deletes",
                },
            },
            "required": ["action"],
        },
    },
}


async def memory_profile_skill(
    action: str = "read",
    key: str = "",
    value: str = "",
    update_action: str = "set",
) -> dict:
    trace_tool = TraceTool()
    semantic_memory = SemanticMemoryService()

    trace = trace_tool.create(task_type="memory_profile", user_input=f"{action} preferences")
    logger.info(f"[Skill:memory_profile trace={trace.trace_id}] action={action} key={key}")

    changes_summary = ""

    if action == "read":
        preferences = await semantic_memory.load_user_preferences()

        # Also load raw prefs
        raw_prefs = await _load_raw_preferences()

        await trace_tool.complete(trace.trace_id, status="success", trace=trace)

        return {
            "success": True,
            "trace_id": trace.trace_id,
            "action": "read",
            "preferences": {**preferences, **raw_prefs},
            "message": "当前偏好设置已获取",
        }

    if action == "update" and key:
        changes_summary = await _update_preference(key, value, update_action)
        await trace_tool.log_step(
            trace_id=trace.trace_id,
            step_name="update_preferences",
            input_summary=f"key={key}, value={value}, action={update_action}",
            output_summary=changes_summary,
        )

    # Read updated preferences
    preferences = await semantic_memory.load_user_preferences()
    raw_prefs = await _load_raw_preferences()

    await trace_tool.complete(trace.trace_id, status="success", trace=trace)

    return {
        "success": True,
        "trace_id": trace.trace_id,
        "action": action,
        "preferences": {**preferences, **raw_prefs},
        "changes_summary": changes_summary,
        "message": changes_summary or "偏好未更改",
    }


async def _load_raw_preferences() -> dict:
    prefs = {}
    try:
        async with async_session() as session:
            result = await session.execute(select(UserPreference))
            for row in result.scalars().all():
                if row.key not in ("preferred_categories", "preferred_topics", "topic_interest_weights"):
                    prefs[row.key] = row.value
    except Exception:
        pass
    return prefs


async def _update_preference(key: str, value: str, update_action: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        async with async_session() as session:
            result = await session.execute(
                select(UserPreference).where(UserPreference.key == key)
            )
            row = result.scalar_one_or_none()

            if update_action == "set":
                if row:
                    row.value = value
                    row.updated_at = now
                else:
                    session.add(UserPreference(key=key, value=value, updated_at=now))
                await session.commit()
                return f"已将 {key} 设置为 {value}"

            if update_action == "append":
                current = row.value if row else ""
                items = [s.strip() for s in current.split(",") if s.strip()]
                if value not in items:
                    items.append(value)
                new_value = ", ".join(items)
                if row:
                    row.value = new_value
                    row.updated_at = now
                else:
                    session.add(UserPreference(key=key, value=new_value, updated_at=now))
                await session.commit()
                return f"已将 {value} 添加到 {key}"

            if update_action == "remove":
                if row:
                    items = [s.strip() for s in row.value.split(",") if s.strip()]
                    if value in items:
                        items.remove(value)
                    row.value = ", ".join(items)
                    row.updated_at = now
                    await session.commit()
                    return f"已从 {key} 移除 {value}"
                return f"{key} 中未找到 {value}"

            return f"未知操作: {update_action}"

    except Exception as exc:
        logger.error(f"Failed to update preference {key}: {exc}")
        return f"更新 {key} 失败: {exc}"
