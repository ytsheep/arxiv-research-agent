"""Settings API routes."""

from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import select
from app.db.database import async_session
from app.models.settings import UserPreference
from app.core.config import settings

router = APIRouter()

DEFAULT_PREFERENCES = {
    "default_candidate_k": "20",
    "default_top_n": "2",
    "preferred_categories": "",
    "preferred_topics": "",
    "summary_language": "zh-CN",
    "auto_parse_full_text": "false",
}


def _llm_status() -> dict:
    """Get actual LLM configuration status from environment."""
    return {
        "llm_provider": settings.llm_provider or "openai",
        "llm_model": settings.llm_model or "",
        "llm_api_key_set": bool(settings.llm_api_key),
        "llm_available": bool(settings.llm_api_key),
    }


@router.get("/api/settings/preferences")
async def get_preferences():
    """Get all user preferences."""
    try:
        async with async_session() as session:
            result = await session.execute(select(UserPreference))
            rows = result.scalars().all()

        prefs = {r.key: r.value for r in rows}
        merged = {**DEFAULT_PREFERENCES, **prefs, **_llm_status()}
        return {"success": True, "preferences": merged}

    except Exception as e:
        return {"success": True, "preferences": {**DEFAULT_PREFERENCES, **_llm_status()}}


@router.put("/api/settings/preferences")
async def update_preferences(preferences: dict):
    """Update user preferences."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        async with async_session() as session:
            for key, value in preferences.items():
                if key.startswith("_"):
                    continue
                value_str = str(value).lower() if isinstance(value, bool) else str(value)

                existing = await session.execute(
                    select(UserPreference).where(UserPreference.key == key)
                )
                row = existing.scalar_one_or_none()

                if row:
                    row.value = value_str
                    row.updated_at = now
                else:
                    row = UserPreference(key=key, value=value_str, updated_at=now)
                    session.add(row)

            await session.commit()
        return {"success": True, "message": "Preferences updated"}

    except Exception as e:
        return {"success": False, "message": str(e)}
