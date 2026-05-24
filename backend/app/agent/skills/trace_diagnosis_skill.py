"""Trace Diagnosis Skill: query and diagnose task execution traces.

Wraps: trace.query → (if failed) → trace.get → summarize failure.
"""

from app.tools.trace_tool import TraceTool
from app.core.logging import logger


TRACE_DIAGNOSIS_SKILL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "trace_diagnosis_skill",
        "description": "Query task execution traces and diagnose failures. Search by keyword, task type, or status. Returns trace summaries and failure analysis.",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Search keyword for user_input or summary",
                },
                "task_type": {
                    "type": "string",
                    "description": "Filter by task type: chat, paper_search, paper_collect, paper_parse, subscription_run",
                },
                "status": {
                    "type": "string",
                    "description": "Filter by status: running, success, failed",
                },
                "page": {
                    "type": "integer",
                    "description": "Page number (default 1)",
                    "default": 1,
                },
                "page_size": {
                    "type": "integer",
                    "description": "Results per page (default 20)",
                    "default": 20,
                },
            },
        },
    },
}


async def trace_diagnosis_skill(
    keyword: str = "",
    task_type: str = "",
    status: str = "",
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """Query traces and optionally diagnose failures."""
    trace_tool = TraceTool()

    query_result = await trace_tool.query(
        keyword=keyword,
        task_type=task_type,
        status=status,
        page=page,
        page_size=page_size,
    )

    traces = query_result.get("traces", [])

    # For failed traces, attach a diagnosis summary
    diagnoses = []
    for t in traces:
        if t.get("status") == "failed" and t.get("error_message"):
            diagnoses.append({
                "trace_id": t.get("trace_id"),
                "failed_step": t.get("error_message"),
                "suggestion": _suggest_fix(t.get("task_type", ""), t.get("error_message", "")),
            })

    return {
        "success": True,
        "total": query_result.get("total", 0),
        "traces": traces,
        "diagnoses": diagnoses,
        "message": f"Found {query_result.get('total', 0)} traces"
                   + (f", {len(diagnoses)} failed" if diagnoses else ""),
    }


def _suggest_fix(task_type: str, error_message: str) -> str:
    """Suggest a fix based on common failure patterns."""
    msg_lower = error_message.lower()
    if "429" in msg_lower or "rate" in msg_lower:
        return "arXiv API 限流，请稍后重试或减少请求频率"
    if "timeout" in msg_lower:
        return "外部服务超时，请检查网络连接或稍后重试"
    if "pdf" in msg_lower and ("download" in msg_lower or "parse" in msg_lower):
        return "PDF 下载或解析失败，请检查 arXiv PDF 链接是否有效"
    if "email" in msg_lower or "smtp" in msg_lower:
        return "邮件发送失败，请检查 SMTP 配置"
    if "feishu" in msg_lower or "webhook" in msg_lower:
        return "飞书推送失败，请检查 Webhook 地址"
    return "请查看完整 trace 步骤定位问题"
