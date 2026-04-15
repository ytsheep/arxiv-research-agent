from __future__ import annotations

import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.config import Settings
from app.db.database import SessionLocal, session_scope
from app.db.models import DigestDelivery, DigestRun, DigestRunItem, Subscription
from app.models import DeliveryResult, DigestResult, Paper
from app.services.notification_service import NotificationManager
from app.services.subscription_service import SubscriptionService
from app.workflows import ArxivResearchWorkflow


logger = logging.getLogger(__name__)

DEFAULT_MAX_RESULTS = 50
DEFAULT_TOP_K = 5


class DailyDigestService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.workflow = ArxivResearchWorkflow(settings)
        self.notification_manager = NotificationManager(settings)
        self.subscription_service = SubscriptionService(settings)
        self._schedule_lock = threading.Lock()

    def generate_digest(
        self,
        query: str | None = None,
        focus: str | None = None,
        keywords: list[str] | None = None,
        max_results: int | None = None,
        top_k: int | None = None,
        api_key: str | None = None,
    ) -> DigestResult:
        resolved_query = self.subscription_service.build_effective_query(query, keywords or [])
        resolved_focus = (focus or "").strip()
        if not resolved_focus:
            raise ValueError("Focus is required.")

        resolved_api_key = api_key or self.settings.dashscope_api_key
        if not resolved_api_key:
            raise ValueError("DASHSCOPE_API_KEY is required to run the research workflow.")

        return self.workflow.run(
            query=resolved_query,
            focus=resolved_focus,
            api_key=resolved_api_key,
            max_results=max_results or DEFAULT_MAX_RESULTS,
            top_k=top_k or DEFAULT_TOP_K,
        )

    def run_subscription(
        self,
        subscription_id: int,
        *,
        notify: bool = True,
        api_key: str | None = None,
        trigger_mode: str = "manual",
        scheduled_for_date: date | None = None,
    ) -> DigestResult:
        snapshot = self.subscription_service.get_subscription_snapshot(subscription_id)
        if not snapshot.enabled and trigger_mode == "scheduled":
            raise ValueError(f"Subscription {subscription_id} is disabled.")

        run_id = self._create_run_record(
            subscription_id=subscription_id,
            trigger_mode=trigger_mode,
            scheduled_for_date=scheduled_for_date,
        )
        if run_id is None:
            raise ValueError(f"Subscription {subscription_id} has already run for {scheduled_for_date}.")

        try:
            effective_query = self.subscription_service.build_effective_query(snapshot.query, snapshot.keywords)
            candidate_top_k = self._candidate_top_k(snapshot.top_k)
            raw_result = self.workflow.run(
                query=effective_query,
                focus=snapshot.focus,
                api_key=api_key or self.settings.dashscope_api_key,
                max_results=snapshot.max_results,
                top_k=candidate_top_k,
            )
            recent_paper_ids = self._load_recent_paper_ids(subscription_id, snapshot.dedupe_days)
            final_papers = self._filter_papers(
                papers=raw_result.papers,
                top_k=snapshot.top_k,
                recent_paper_ids=recent_paper_ids,
            )
            final_result = self.workflow.render_digest_result(
                query=effective_query,
                focus=snapshot.focus,
                papers=final_papers,
                tool_trace=raw_result.tool_trace,
                agent_summary=raw_result.agent_summary,
                generated_at=raw_result.generated_at,
                subscription_id=snapshot.id,
                subscription_name=snapshot.name,
            )

            delivery_results: list[DeliveryResult] = []
            if notify and snapshot.recipients:
                delivery_results = self.notification_manager.notify_digest(final_result, snapshot.recipients)

            updated_result = final_result.model_copy(
                update={
                    "delivery_results": delivery_results,
                    "notified_channels": sorted(
                        {delivery.channel for delivery in delivery_results if delivery.status == "success"}
                    ),
                }
            )
            self._finalize_run(
                run_id=run_id,
                subscription_id=subscription_id,
                result=updated_result,
                recipients=snapshot.recipients,
            )
            return updated_result
        except Exception as exc:
            self._mark_run_failed(run_id=run_id, error_message=str(exc))
            raise

    def run_due_subscriptions(self) -> None:
        if not self._schedule_lock.acquire(blocking=False):
            logger.warning("Scheduled digest scan skipped because another scan is still running.")
            return

        try:
            now_utc = datetime.now(UTC)
            due_subscriptions = []
            for subscription in self.subscription_service.list_enabled_subscriptions():
                local_now = now_utc.astimezone(self._resolve_timezone(subscription.timezone))
                if (
                    local_now.hour == subscription.schedule_hour
                    and local_now.minute == subscription.schedule_minute
                ):
                    due_subscriptions.append((subscription.id, local_now.date()))

            if not due_subscriptions:
                logger.info("No due subscriptions found for current scheduler tick.")
                return

            with ThreadPoolExecutor(max_workers=max(1, self.settings.scheduler_max_workers)) as executor:
                futures = {
                    executor.submit(
                        self._run_scheduled_subscription,
                        subscription_id,
                        scheduled_date,
                    ): subscription_id
                    for subscription_id, scheduled_date in due_subscriptions
                }
                for future in as_completed(futures):
                    subscription_id = futures[future]
                    try:
                        future.result()
                        logger.info("Scheduled subscription %s completed.", subscription_id)
                    except Exception as exc:
                        logger.exception("Scheduled subscription %s failed: %s", subscription_id, exc)
        finally:
            self._schedule_lock.release()

    def _run_scheduled_subscription(self, subscription_id: int, scheduled_date: date) -> None:
        try:
            self.run_subscription(
                subscription_id=subscription_id,
                notify=True,
                trigger_mode="scheduled",
                scheduled_for_date=scheduled_date,
            )
        except ValueError as exc:
            logger.info("Scheduled subscription %s skipped: %s", subscription_id, exc)

    @staticmethod
    def _candidate_top_k(top_k: int) -> int:
        return min(20, max(top_k * 3, top_k + 5))

    def _resolve_timezone(self, timezone_name: str) -> ZoneInfo:
        try:
            return ZoneInfo(timezone_name)
        except Exception:
            logger.warning("Invalid subscription timezone '%s', falling back to %s.", timezone_name, self.settings.timezone)
            return ZoneInfo(self.settings.timezone)

    @staticmethod
    def _filter_papers(
        *,
        papers: list[Paper],
        top_k: int,
        recent_paper_ids: set[str],
    ) -> list[Paper]:
        unique_papers: list[Paper] = []
        seen_ids: set[str] = set()
        for paper in papers:
            if paper.id in seen_ids or paper.id in recent_paper_ids:
                continue
            seen_ids.add(paper.id)
            unique_papers.append(paper)
            if len(unique_papers) >= top_k:
                break
        return unique_papers

    def _load_recent_paper_ids(self, subscription_id: int, dedupe_days: int) -> set[str]:
        threshold = datetime.utcnow() - timedelta(days=dedupe_days)
        with session_scope() as session:
            stmt = (
                select(DigestRunItem.paper_id)
                .join(DigestRun, DigestRun.id == DigestRunItem.digest_run_id)
                .where(DigestRunItem.subscription_id == subscription_id)
                .where(DigestRun.status.in_(["success", "partial"]))
                .where(DigestRunItem.created_at >= threshold)
            )
            return set(session.scalars(stmt).all())

    def _create_run_record(
        self,
        *,
        subscription_id: int,
        trigger_mode: str,
        scheduled_for_date: date | None,
    ) -> int | None:
        with session_scope() as session:
            run = DigestRun(
                subscription_id=subscription_id,
                trigger_mode=trigger_mode,
                scheduled_for_date=scheduled_for_date,
                status="running",
            )
            session.add(run)
            try:
                session.flush()
            except IntegrityError:
                session.rollback()
                return None
            return run.id

    def _finalize_run(
        self,
        *,
        run_id: int,
        subscription_id: int,
        result: DigestResult,
        recipients: list[dict],
    ) -> None:
        with session_scope() as session:
            run = session.get(DigestRun, run_id)
            if not run:
                return

            for paper in result.papers:
                session.add(
                    DigestRunItem(
                        digest_run_id=run_id,
                        subscription_id=subscription_id,
                        paper_id=paper.id,
                        title=paper.title,
                        entry_url=paper.entry_url,
                        published=paper.published,
                    )
                )

            recipient_id_map = {
                (recipient["channel"], recipient["target"]): recipient.get("id")
                for recipient in recipients
            }
            for delivery in result.delivery_results:
                session.add(
                    DigestDelivery(
                        digest_run_id=run_id,
                        recipient_id=recipient_id_map.get((delivery.channel, delivery.target)),
                        channel=delivery.channel,
                        target=delivery.target,
                        status=delivery.status,
                        error_message=delivery.error_message,
                    )
                )

            success_count = len([item for item in result.delivery_results if item.status == "success"])
            failed_count = len([item for item in result.delivery_results if item.status == "failed"])
            if result.delivery_results:
                if success_count and failed_count:
                    status = "partial"
                elif success_count:
                    status = "success"
                else:
                    status = "failed"
            else:
                status = "success"

            run.status = status
            run.papers_count = len(result.papers)
            run.error_message = self._collect_delivery_errors(result.delivery_results)
            run.finished_at = datetime.utcnow()

    def _mark_run_failed(self, *, run_id: int, error_message: str) -> None:
        with session_scope() as session:
            run = session.get(DigestRun, run_id)
            if not run:
                return
            run.status = "failed"
            run.error_message = error_message
            run.finished_at = datetime.utcnow()

    @staticmethod
    def _collect_delivery_errors(deliveries: list[DeliveryResult]) -> str | None:
        errors = [
            f"{delivery.channel}:{delivery.target} -> {delivery.error_message}"
            for delivery in deliveries
            if delivery.status == "failed" and delivery.error_message
        ]
        return "\n".join(errors) if errors else None
