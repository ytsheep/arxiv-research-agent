from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.contracts import (
    RecipientPayload,
    SubscriptionCreateRequest,
    SubscriptionRecipientResponse,
    SubscriptionResponse,
    SubscriptionUpdateRequest,
)
from app.config import Settings
from app.db.database import SessionLocal, session_scope
from app.db.models import DigestRun, Subscription, SubscriptionKeyword, SubscriptionRecipient


@dataclass
class SubscriptionSnapshot:
    id: int
    name: str
    query: str | None
    keywords: list[str]
    focus: str
    top_k: int
    max_results: int
    schedule_hour: int
    schedule_minute: int
    timezone: str
    dedupe_days: int
    enabled: bool
    recipients: list[dict[str, object]]


class SubscriptionService:
    def __init__(self, settings: Settings):
        self.settings = settings

    @staticmethod
    def build_effective_query(query: str | None, keywords: Iterable[str]) -> str:
        cleaned_query = (query or "").strip()
        if cleaned_query:
            return cleaned_query

        cleaned_keywords = [keyword.strip() for keyword in keywords if keyword and keyword.strip()]
        unique_keywords: list[str] = []
        for keyword in cleaned_keywords:
            if keyword not in unique_keywords:
                unique_keywords.append(keyword)

        if not unique_keywords:
            raise ValueError("Please provide either a query or at least one keyword.")

        parts = [f'all:"{keyword}"' for keyword in unique_keywords]
        return " OR ".join(parts)

    def list_subscriptions(self) -> List[SubscriptionResponse]:
        with session_scope() as session:
            stmt = (
                select(Subscription)
                .options(
                    joinedload(Subscription.keywords),
                    joinedload(Subscription.recipients),
                )
                .order_by(Subscription.created_at.desc())
            )
            subscriptions = session.scalars(stmt).unique().all()
            return [self._to_response(subscription) for subscription in subscriptions]

    def get_subscription_or_raise(self, subscription_id: int) -> SubscriptionResponse:
        with session_scope() as session:
            subscription = self._fetch_subscription(session, subscription_id)
            return self._to_response(subscription)

    def get_subscription_snapshot(self, subscription_id: int) -> SubscriptionSnapshot:
        with session_scope() as session:
            subscription = self._fetch_subscription(session, subscription_id)
            return self._to_snapshot(subscription)

    def create_subscription(self, payload: SubscriptionCreateRequest) -> SubscriptionResponse:
        effective_query = self.build_effective_query(payload.query, payload.keywords)
        with session_scope() as session:
            subscription = Subscription(
                name=payload.name.strip(),
                query=(payload.query or "").strip() or None,
                focus=payload.focus.strip(),
                top_k=payload.top_k,
                max_results=payload.max_results,
                schedule_hour=payload.schedule_hour,
                schedule_minute=payload.schedule_minute,
                timezone=payload.timezone.strip() or self.settings.timezone,
                dedupe_days=payload.dedupe_days,
                enabled=payload.enabled,
            )
            subscription.keywords = self._build_keywords(payload.keywords)
            subscription.recipients = self._build_recipients(payload.recipients)
            session.add(subscription)
            session.flush()
            session.refresh(subscription)
            session.refresh(subscription, attribute_names=["keywords", "recipients"])
            return self._to_response(subscription, effective_query=effective_query)

    def update_subscription(self, subscription_id: int, payload: SubscriptionUpdateRequest) -> SubscriptionResponse:
        with session_scope() as session:
            subscription = self._fetch_subscription(session, subscription_id)

            if payload.name is not None:
                subscription.name = payload.name.strip()
            if payload.query is not None:
                subscription.query = payload.query.strip() or None
            if payload.focus is not None:
                subscription.focus = payload.focus.strip()
            if payload.top_k is not None:
                subscription.top_k = payload.top_k
            if payload.max_results is not None:
                subscription.max_results = payload.max_results
            if payload.schedule_hour is not None:
                subscription.schedule_hour = payload.schedule_hour
            if payload.schedule_minute is not None:
                subscription.schedule_minute = payload.schedule_minute
            if payload.timezone is not None:
                subscription.timezone = payload.timezone.strip() or self.settings.timezone
            if payload.dedupe_days is not None:
                subscription.dedupe_days = payload.dedupe_days
            if payload.enabled is not None:
                subscription.enabled = payload.enabled
            if payload.keywords is not None:
                subscription.keywords.clear()
                subscription.keywords.extend(self._build_keywords(payload.keywords))
            if payload.recipients is not None:
                subscription.recipients.clear()
                subscription.recipients.extend(self._build_recipients(payload.recipients))

            effective_query = self.build_effective_query(
                subscription.query,
                [keyword.keyword for keyword in subscription.keywords],
            )
            session.flush()
            session.refresh(subscription, attribute_names=["keywords", "recipients"])
            return self._to_response(subscription, effective_query=effective_query)

    def delete_subscription(self, subscription_id: int) -> None:
        with session_scope() as session:
            subscription = self._fetch_subscription(session, subscription_id)
            session.delete(subscription)

    def list_runs(self, subscription_id: int, limit: int = 20) -> List[DigestRun]:
        with session_scope() as session:
            self._fetch_subscription(session, subscription_id)
            stmt = (
                select(DigestRun)
                .where(DigestRun.subscription_id == subscription_id)
                .order_by(DigestRun.started_at.desc())
                .limit(limit)
            )
            return list(session.scalars(stmt).all())

    def list_enabled_subscriptions(self) -> List[SubscriptionSnapshot]:
        with session_scope() as session:
            stmt = (
                select(Subscription)
                .options(
                    joinedload(Subscription.keywords),
                    joinedload(Subscription.recipients),
                )
                .where(Subscription.enabled.is_(True))
            )
            subscriptions = session.scalars(stmt).unique().all()
            return [self._to_snapshot(subscription) for subscription in subscriptions]

    @staticmethod
    def _build_keywords(keywords: Iterable[str]) -> List[SubscriptionKeyword]:
        cleaned = []
        for keyword in keywords:
            normalized = keyword.strip()
            if normalized and normalized not in cleaned:
                cleaned.append(normalized)
        return [
            SubscriptionKeyword(keyword=keyword, sort_order=index)
            for index, keyword in enumerate(cleaned)
        ]

    @staticmethod
    def _build_recipients(recipients: Iterable[RecipientPayload]) -> List[SubscriptionRecipient]:
        return [
            SubscriptionRecipient(
                channel=recipient.channel,
                target=recipient.target.strip(),
                enabled=recipient.enabled,
            )
            for recipient in recipients
            if recipient.target.strip()
        ]

    def _fetch_subscription(self, session, subscription_id: int) -> Subscription:
        stmt = (
            select(Subscription)
            .options(joinedload(Subscription.keywords), joinedload(Subscription.recipients))
            .where(Subscription.id == subscription_id)
        )
        subscription = session.scalars(stmt).unique().first()
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found.")
        return subscription

    def _to_response(
        self,
        subscription: Subscription,
        *,
        effective_query: str | None = None,
    ) -> SubscriptionResponse:
        resolved_query = effective_query or self.build_effective_query(
            subscription.query,
            [keyword.keyword for keyword in subscription.keywords],
        )
        return SubscriptionResponse(
            id=subscription.id,
            name=subscription.name,
            query=subscription.query,
            effective_query=resolved_query,
            keywords=[keyword.keyword for keyword in subscription.keywords],
            focus=subscription.focus,
            top_k=subscription.top_k,
            max_results=subscription.max_results,
            schedule_hour=subscription.schedule_hour,
            schedule_minute=subscription.schedule_minute,
            timezone=subscription.timezone,
            dedupe_days=subscription.dedupe_days,
            enabled=subscription.enabled,
            recipients=[
                SubscriptionRecipientResponse(
                    id=recipient.id,
                    channel=recipient.channel,
                    target=recipient.target,
                    enabled=recipient.enabled,
                )
                for recipient in subscription.recipients
            ],
            created_at=subscription.created_at,
            updated_at=subscription.updated_at,
        )

    def _to_snapshot(self, subscription: Subscription) -> SubscriptionSnapshot:
        return SubscriptionSnapshot(
            id=subscription.id,
            name=subscription.name,
            query=subscription.query,
            keywords=[keyword.keyword for keyword in subscription.keywords],
            focus=subscription.focus,
            top_k=subscription.top_k,
            max_results=subscription.max_results,
            schedule_hour=subscription.schedule_hour,
            schedule_minute=subscription.schedule_minute,
            timezone=subscription.timezone,
            dedupe_days=subscription.dedupe_days,
            enabled=subscription.enabled,
            recipients=[
                {
                    "id": recipient.id,
                    "channel": recipient.channel,
                    "target": recipient.target,
                    "enabled": recipient.enabled,
                }
                for recipient in subscription.recipients
                if recipient.enabled
            ],
        )
