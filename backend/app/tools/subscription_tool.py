"""Subscription tool: manage subscription tasks with database persistence."""

from __future__ import annotations
import json
from datetime import datetime
from sqlalchemy import select, update, delete
from app.db.database import async_session
from app.models.subscription import Subscription, SubscriptionRun
from app.core.logging import logger


class SubscriptionTool:
    async def create(self, **kwargs) -> dict:
        """Create a new subscription."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            async with async_session() as session:
                sub = Subscription(
                    name=kwargs.get("name", ""),
                    candidate_k=kwargs.get("candidate_k", 20),
                    top_n=kwargs.get("top_n", 2),
                    cron_expr=kwargs.get("cron_expr", "0 8 * * *"),
                    timezone=kwargs.get("timezone", "Asia/Shanghai"),
                    email_enabled=1 if kwargs.get("email_enabled") else 0,
                    email_to=kwargs.get("email_to", ""),
                    feishu_enabled=1 if kwargs.get("feishu_enabled") else 0,
                    feishu_webhook_ref=kwargs.get("feishu_webhook_ref", ""),
                    auto_parse_full_text=1 if kwargs.get("auto_parse_full_text") else 0,
                    enabled=1 if kwargs.get("enabled", True) else 0,
                    created_at=now,
                    updated_at=now,
                )
                sub.set_topics(kwargs.get("topics", []))
                sub.set_categories_list(kwargs.get("categories", []))
                session.add(sub)
                await session.commit()
                await session.refresh(sub)

                logger.info(f"Subscription created: id={sub.id}, name={sub.name}")
                return {"success": True, "subscription_id": sub.id, "error": None}

        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            return {"success": False, "subscription_id": 0, "error": str(e)}

    async def list(self, enabled: bool | None = None) -> dict:
        """List all subscriptions."""
        try:
            async with async_session() as session:
                query = select(Subscription)
                if enabled is not None:
                    query = query.where(Subscription.enabled == (1 if enabled else 0))
                query = query.order_by(Subscription.created_at.desc())
                result = await session.execute(query)
                subs = result.scalars().all()

                items = []
                for s in subs:
                    items.append({
                        "id": s.id,
                        "name": s.name,
                        "topics": s.get_topics(),
                        "categories": s.get_categories_list(),
                        "candidate_k": s.candidate_k,
                        "top_n": s.top_n,
                        "cron_expr": s.cron_expr,
                        "timezone": s.timezone,
                        "email_enabled": bool(s.email_enabled),
                        "email_to": s.email_to or "",
                        "feishu_enabled": bool(s.feishu_enabled),
                        "feishu_webhook_ref": s.feishu_webhook_ref or "",
                        "auto_parse_full_text": bool(s.auto_parse_full_text),
                        "enabled": bool(s.enabled),
                        "created_at": s.created_at or "",
                        "updated_at": s.updated_at or "",
                    })

                return {"success": True, "subscriptions": items}

        except Exception as e:
            logger.error(f"Failed to list subscriptions: {e}")
            return {"success": False, "subscriptions": []}

    async def update(self, subscription_id: int, patch: dict) -> dict:
        """Update an existing subscription."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            async with async_session() as session:
                result = await session.execute(
                    select(Subscription).where(Subscription.id == subscription_id)
                )
                sub = result.scalar_one_or_none()
                if not sub:
                    return {"success": False, "error": "SUBSCRIPTION_NOT_FOUND"}

                field_map = {
                    "name": "name",
                    "candidate_k": "candidate_k",
                    "top_n": "top_n",
                    "cron_expr": "cron_expr",
                    "timezone": "timezone",
                    "email_to": "email_to",
                    "feishu_webhook_ref": "feishu_webhook_ref",
                }
                for patch_key, model_attr in field_map.items():
                    if patch_key in patch:
                        setattr(sub, model_attr, patch[patch_key])

                if "topics" in patch:
                    sub.set_topics(patch["topics"])
                if "categories" in patch:
                    sub.set_categories_list(patch["categories"])
                if "email_enabled" in patch:
                    sub.email_enabled = 1 if patch["email_enabled"] else 0
                if "feishu_enabled" in patch:
                    sub.feishu_enabled = 1 if patch["feishu_enabled"] else 0
                if "auto_parse_full_text" in patch:
                    sub.auto_parse_full_text = 1 if patch["auto_parse_full_text"] else 0
                if "enabled" in patch:
                    sub.enabled = 1 if patch["enabled"] else 0

                sub.updated_at = now
                await session.commit()
                return {"success": True, "error": None}

        except Exception as e:
            logger.error(f"Failed to update subscription {subscription_id}: {e}")
            return {"success": False, "error": str(e)}

    async def delete(self, subscription_id: int) -> dict:
        """Delete a subscription."""
        try:
            async with async_session() as session:
                result = await session.execute(
                    select(Subscription).where(Subscription.id == subscription_id)
                )
                sub = result.scalar_one_or_none()
                if not sub:
                    return {"success": False, "error": "SUBSCRIPTION_NOT_FOUND"}

                await session.delete(sub)
                await session.commit()
                logger.info(f"Subscription {subscription_id} deleted")
                return {"success": True, "error": None}

        except Exception as e:
            logger.error(f"Failed to delete subscription {subscription_id}: {e}")
            return {"success": False, "error": str(e)}

    async def get(self, subscription_id: int) -> dict:
        """Get a single subscription by ID."""
        try:
            async with async_session() as session:
                result = await session.execute(
                    select(Subscription).where(Subscription.id == subscription_id)
                )
                sub = result.scalar_one_or_none()
                if not sub:
                    return {"success": False, "subscription": None, "error": "NOT_FOUND"}

                return {
                    "success": True,
                    "subscription": {
                        "id": sub.id,
                        "name": sub.name,
                        "topics": sub.get_topics(),
                        "categories": sub.get_categories_list(),
                        "candidate_k": sub.candidate_k,
                        "top_n": sub.top_n,
                        "cron_expr": sub.cron_expr,
                        "timezone": sub.timezone,
                        "email_enabled": bool(sub.email_enabled),
                        "email_to": sub.email_to or "",
                        "feishu_enabled": bool(sub.feishu_enabled),
                        "feishu_webhook_ref": sub.feishu_webhook_ref or "",
                        "auto_parse_full_text": bool(sub.auto_parse_full_text),
                        "enabled": bool(sub.enabled),
                        "created_at": sub.created_at or "",
                        "updated_at": sub.updated_at or "",
                    },
                }

        except Exception as e:
            logger.error(f"Failed to get subscription {subscription_id}: {e}")
            return {"success": False, "subscription": None, "error": str(e)}

    async def record_run(
        self,
        subscription_id: int,
        run_date: str,
        selected_papers: list[dict],
        sent_email: bool = False,
        sent_feishu: bool = False,
        status: str = "running",
        error_message: str = "",
        trace_id: str = "",
    ) -> int:
        """Record a subscription run."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            async with async_session() as session:
                run = SubscriptionRun(
                    subscription_id=subscription_id,
                    run_date=run_date,
                    selected_papers=json.dumps(selected_papers, ensure_ascii=False),
                    sent_email=1 if sent_email else 0,
                    sent_feishu=1 if sent_feishu else 0,
                    status=status,
                    error_message=error_message,
                    trace_id=trace_id,
                    created_at=now,
                )
                session.add(run)
                await session.commit()
                await session.refresh(run)
                return run.id

        except Exception as e:
            logger.error(f"Failed to record subscription run: {e}")
            return 0
