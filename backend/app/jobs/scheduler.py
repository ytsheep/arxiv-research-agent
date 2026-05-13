"""APScheduler setup for daily subscription jobs."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.tools.subscription_tool import SubscriptionTool
from app.jobs.daily_subscription_job import run_daily_subscription
from app.core.logging import logger

scheduler = AsyncIOScheduler()
_job_ids: dict[int, str] = {}


async def _run_subscription(subscription_id: int):
    """Wrapper to run a subscription job."""
    logger.info(f"Starting scheduled run for subscription {subscription_id}")
    await run_daily_subscription(subscription_id)


def add_subscription_job(subscription_id: int, cron_expr: str, timezone: str = "Asia/Shanghai"):
    """Add or update a subscription job in the scheduler."""
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        logger.error(f"Invalid cron expression: {cron_expr}")
        return

    try:
        minute, hour, day, month, day_of_week = parts
        trigger = CronTrigger(
            minute=minute, hour=hour, day=day, month=month,
            day_of_week=day_of_week, timezone=timezone,
        )

        # Remove existing job if present
        if subscription_id in _job_ids:
            try:
                scheduler.remove_job(_job_ids[subscription_id])
            except Exception:
                pass

        job_id = f"sub_{subscription_id}"
        _job_ids[subscription_id] = job_id

        scheduler.add_job(
            _run_subscription,
            trigger=trigger,
            args=[subscription_id],
            id=job_id,
            replace_existing=True,
        )
        logger.info(f"Subscription job added: id={subscription_id}, cron={cron_expr}")

    except Exception as e:
        logger.error(f"Failed to add subscription job {subscription_id}: {e}")


def remove_subscription_job(subscription_id: int):
    """Remove a subscription job from the scheduler."""
    if subscription_id in _job_ids:
        try:
            scheduler.remove_job(_job_ids[subscription_id])
        except Exception:
            pass
        del _job_ids[subscription_id]
        logger.info(f"Subscription job removed: id={subscription_id}")


async def start_scheduler():
    """Start the scheduler and load all active subscriptions."""
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")

    # Load existing subscriptions
    sub_tool = SubscriptionTool()
    result = await sub_tool.list(enabled=True)
    for sub in result.get("subscriptions", []):
        add_subscription_job(
            subscription_id=sub["id"],
            cron_expr=sub.get("cron_expr", "0 8 * * *"),
            timezone=sub.get("timezone", "Asia/Shanghai"),
        )


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shut down")
