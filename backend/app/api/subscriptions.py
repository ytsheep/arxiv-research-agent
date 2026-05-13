"""Subscription API routes."""

from fastapi import APIRouter, Query
from app.schemas.paper import OperationResponse
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate
from app.tools.subscription_tool import SubscriptionTool
from app.jobs.daily_subscription_job import run_daily_subscription
from app.jobs.scheduler import add_subscription_job, remove_subscription_job

router = APIRouter()


@router.get("/api/subscriptions")
async def list_subscriptions(enabled: bool | None = Query(None)):
    """List all subscriptions."""
    tool = SubscriptionTool()
    result = await tool.list(enabled=enabled)
    return {"success": result["success"], "subscriptions": result.get("subscriptions", [])}


@router.post("/api/subscriptions")
async def create_subscription(request: SubscriptionCreate):
    """Create a new subscription."""
    tool = SubscriptionTool()
    kwargs = request.model_dump()
    kwargs["email_enabled"] = kwargs.pop("email_enabled", False)
    kwargs["feishu_enabled"] = kwargs.pop("feishu_enabled", False)
    kwargs["auto_parse_full_text"] = kwargs.pop("auto_parse_full_text", False)

    result = await tool.create(**kwargs)

    if result["success"] and result.get("subscription_id"):
        # Add to scheduler
        add_subscription_job(
            subscription_id=result["subscription_id"],
            cron_expr=request.cron_expr,
            timezone=request.timezone,
        )

    return {
        "success": result["success"],
        "subscription_id": result.get("subscription_id", 0),
        "message": "订阅创建成功" if result["success"] else result.get("error", ""),
    }


@router.get("/api/subscriptions/{subscription_id}")
async def get_subscription(subscription_id: int):
    """Get a single subscription."""
    tool = SubscriptionTool()
    result = await tool.get(subscription_id)
    return result


@router.put("/api/subscriptions/{subscription_id}")
async def update_subscription(subscription_id: int, request: SubscriptionUpdate):
    """Update a subscription."""
    tool = SubscriptionTool()
    patch = request.model_dump(exclude_none=True)

    # Convert booleans
    if "email_enabled" in patch:
        patch["email_enabled"] = patch["email_enabled"]
    if "feishu_enabled" in patch:
        patch["feishu_enabled"] = patch["feishu_enabled"]
    if "auto_parse_full_text" in patch:
        patch["auto_parse_full_text"] = patch["auto_parse_full_text"]
    if "enabled" in patch:
        patch["enabled"] = patch["enabled"]

    result = await tool.update(subscription_id, patch)

    # Reschedule if cron or enabled changed
    if result["success"]:
        sub_result = await tool.get(subscription_id)
        if sub_result["success"]:
            sub = sub_result["subscription"]
            if sub["enabled"]:
                add_subscription_job(subscription_id, sub["cron_expr"], sub["timezone"])
            else:
                remove_subscription_job(subscription_id)

    return {
        "success": result["success"],
        "message": "订阅更新成功" if result["success"] else result.get("error", ""),
    }


@router.delete("/api/subscriptions/{subscription_id}")
async def delete_subscription(subscription_id: int):
    """Delete a subscription."""
    tool = SubscriptionTool()
    result = await tool.delete(subscription_id)
    if result["success"]:
        remove_subscription_job(subscription_id)
    return {
        "success": result["success"],
        "message": "订阅已删除" if result["success"] else result.get("error", ""),
    }


@router.post("/api/subscriptions/{subscription_id}/run-now")
async def run_subscription_now(subscription_id: int, dry_run: bool = Query(False)):
    """Run a subscription immediately."""
    result = await run_daily_subscription(subscription_id, dry_run=dry_run)
    return {
        "success": result["success"],
        "trace_id": result.get("trace_id", ""),
        "paper_count": result.get("paper_count", 0),
        "sent_email": result.get("sent_email", False),
        "sent_feishu": result.get("sent_feishu", False),
        "message": (
            f"订阅执行完成，找到 {result.get('paper_count', 0)} 篇论文"
            if result["success"]
            else result.get("error", "执行失败")
        ),
    }
