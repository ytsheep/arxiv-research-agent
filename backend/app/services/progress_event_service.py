"""In-process progress events for SSE chat workflows."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Coroutine
from typing import Any

from app.schemas.stream import ProgressEvent


TERMINAL_EVENTS = {"workflow.completed", "workflow.partial", "workflow.failed"}

NODE_EVENTS = {
    "classify_intent": ("workflow.stage", "正在理解任务"),
    "query_normalize": ("workflow.stage", "正在整理检索关键词"),
    "arxiv_search": ("workflow.stage", "正在检索 arXiv"),
    "paper_rerank": ("workflow.stage", "正在使用 BGE-M3 重排候选论文"),
    "card_summary": ("workflow.stage", "正在生成论文卡片"),
    "build_paper_response": ("workflow.stage", "正在整理搜索结果"),
    "react_plan": ("workflow.stage", "ReAct 正在规划下一步动作"),
    "react_tool_guard": ("workflow.stage", "正在校验工具调用"),
    "react_tool_execute": ("workflow.stage", "正在执行 Agent Skill"),
    "react_observe": ("workflow.stage", "正在检查 Skill 执行结果"),
    "react_final_response": ("workflow.stage", "正在整理最终回答"),
    "react_fail_response": ("workflow.failed", "Agent 执行失败"),
    "supervisor_init": ("workflow.stage", "正在初始化多 Agent 工作流"),
    "supervisor_plan": ("workflow.planned", "Supervisor 已完成任务拆解"),
    "supervisor_dispatch": ("task.started", "Supervisor 已分派下一项任务"),
    "executor_run": ("task.completed", "Executor 已完成当前任务"),
    "reviewer_check": ("task.reviewed", "Reviewer 已检查当前任务结果"),
    "workflow_review": ("workflow.stage", "正在判断整体任务是否完成"),
    "composer_build": ("workflow.composing", "正在生成最终回答"),
    "error_handler": ("workflow.failed", "多 Agent 工作流执行失败"),
}

AGENT_BY_NODE = {
    "supervisor_init": "supervisor",
    "supervisor_plan": "supervisor",
    "supervisor_dispatch": "supervisor",
    "executor_run": "executor",
    "reviewer_check": "reviewer",
    "workflow_review": "reviewer",
    "composer_build": "reviewer",
    "error_handler": "supervisor",
}

TASK_LABELS = {
    "search_papers": "论文搜索",
    "compare_papers": "论文对比",
    "select_best_paper": "选择最佳论文",
    "collect_paper": "收藏论文",
    "deep_read_paper": "生成精读报告",
    "literature_survey": "生成文献综述",
    "recommend_by_interest": "兴趣推荐",
    "trace_diagnosis": "Trace 诊断",
    "memory_profile": "偏好管理",
}


class ProgressEventService:
    def __init__(self):
        self._history: dict[str, list[dict[str, Any]]] = {}
        self._subscribers: dict[str, set[asyncio.Queue]] = {}
        self._results: dict[str, dict[str, Any]] = {}
        self._tasks: dict[str, asyncio.Task] = {}
        self._sequence: dict[str, int] = {}
        self._lock = asyncio.Lock()

    async def publish(self, event: ProgressEvent) -> dict[str, Any]:
        async with self._lock:
            sequence = self._sequence.get(event.trace_id, 0) + 1
            self._sequence[event.trace_id] = sequence
            event.event_id = f"{event.trace_id}:{sequence}"
            data = event.model_dump()
            history = self._history.setdefault(event.trace_id, [])
            history.append(data)
            if len(history) > 200:
                del history[:-200]
            for queue in self._subscribers.get(event.trace_id, set()):
                queue.put_nowait(data)
        return data

    async def publish_state(self, trace_id: str, state: dict[str, Any]) -> None:
        node = state.get("current_node", "")
        if node not in NODE_EVENTS:
            return

        event_type, message = NODE_EVENTS[node]
        task_id = state.get("current_task_id", "")
        task_type = self._task_type(state.get("task_plan", []), task_id)
        if node == "supervisor_dispatch" and task_type:
            message = f"正在执行：{TASK_LABELS.get(task_type, task_type)}"
        elif node == "supervisor_dispatch":
            event_type = "workflow.stage"
            message = "正在检查剩余任务"
        elif node == "executor_run" and task_type:
            message = f"已完成：{TASK_LABELS.get(task_type, task_type)}"
        elif node == "reviewer_check" and state.get("last_review_decision"):
            message = f"Reviewer 决策：{state['last_review_decision']}"

        payload = {
            "intent": state.get("intent", ""),
            "selected_tool": state.get("selected_tool", ""),
            "task_count": len(state.get("task_plan", [])),
            "completed_tasks": list(state.get("completed_tasks", [])),
            "failed_tasks": list(state.get("failed_tasks", [])),
            "review_decision": state.get("last_review_decision", ""),
        }
        await self.publish(ProgressEvent(
            trace_id=trace_id,
            event_type=event_type,
            agent=AGENT_BY_NODE.get(node, "agent"),
            node=node,
            task_id=task_id,
            task_type=task_type,
            status=state.get("status", "running"),
            message=message,
            payload=payload,
        ))

    async def complete(self, trace_id: str, response: dict[str, Any]) -> None:
        self._results[trace_id] = response
        success = bool(response.get("success", False))
        task_summary = response.get("metadata", {}).get("task_summary", [])
        partial = success and any(item.get("status") != "completed" for item in task_summary)
        event_type = "workflow.partial" if partial else "workflow.completed" if success else "workflow.failed"
        await self.publish(ProgressEvent(
            trace_id=trace_id,
            event_type=event_type,
            status="partial" if partial else "success" if success else "failed",
            message=response.get("message", "任务执行完成" if success else "任务执行失败"),
            payload={"response": response},
        ))

    async def fail(self, trace_id: str, message: str) -> None:
        response = {
            "success": False,
            "type": "error",
            "trace_id": trace_id,
            "message": message,
            "papers": [],
        }
        await self.complete(trace_id, response)

    def track_task(self, trace_id: str, coroutine: Coroutine[Any, Any, Any]) -> None:
        task = asyncio.create_task(coroutine)
        self._tasks[trace_id] = task
        task.add_done_callback(lambda _: self._tasks.pop(trace_id, None))

    async def subscribe(
        self,
        trace_id: str,
        last_event_id: str = "",
    ) -> AsyncIterator[dict[str, Any]]:
        queue: asyncio.Queue = asyncio.Queue()
        async with self._lock:
            self._subscribers.setdefault(trace_id, set()).add(queue)
            history = list(self._history.get(trace_id, []))

        try:
            replay = self._events_after(history, last_event_id)
            for event in replay:
                yield event
            if replay and replay[-1].get("event_type") in TERMINAL_EVENTS:
                return

            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15)
                except asyncio.TimeoutError:
                    yield ProgressEvent(
                        trace_id=trace_id,
                        event_type="heartbeat",
                        message="任务仍在执行",
                    ).model_dump()
                    continue
                yield event
                if event.get("event_type") in TERMINAL_EVENTS:
                    return
        finally:
            async with self._lock:
                subscribers = self._subscribers.get(trace_id, set())
                subscribers.discard(queue)
                if not subscribers:
                    self._subscribers.pop(trace_id, None)

    def get_result(self, trace_id: str) -> dict[str, Any] | None:
        return self._results.get(trace_id)

    def is_known(self, trace_id: str) -> bool:
        return trace_id in self._history or trace_id in self._tasks or trace_id in self._results

    async def close(self) -> None:
        tasks = list(self._tasks.values())
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    @staticmethod
    def _task_type(task_plan: list[dict], task_id: str) -> str:
        for item in task_plan:
            if item.get("task_id") == task_id:
                return item.get("task_type", "")
        return ""

    @staticmethod
    def _events_after(history: list[dict[str, Any]], last_event_id: str) -> list[dict[str, Any]]:
        if not last_event_id:
            return history
        for index, event in enumerate(history):
            if event.get("event_id") == last_event_id:
                return history[index + 1:]
        return history


progress_event_service = ProgressEventService()
