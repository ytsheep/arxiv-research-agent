"""Trace tool: creates and manages trace records with database persistence."""

import uuid
from datetime import datetime
from sqlalchemy import select, func
from app.db.database import async_session
from app.models.trace import Task, TaskStep
from app.core.logging import logger


class Trace:
    """Lightweight trace wrapper. Persists to DB on complete and on each step."""

    def __init__(self, trace_id: str, task_type: str, user_input: str = "", tags: list[str] | None = None):
        self.trace_id = trace_id
        self.task_type = task_type
        self.user_input = user_input
        self.tags = tags or []
        self.tags.append(task_type)
        self.status = "running"
        self.started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ended_at = ""
        self.duration_ms = 0
        self.error_message = ""
        self.steps: list[dict] = []

    @property
    def summary(self):
        return ""

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "task_type": self.task_type,
            "user_input": self.user_input,
            "summary": self.summary,
            "tags": self.tags,
            "status": self.status,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
            "steps": self.steps,
        }


class TraceTool:
    """Database-backed trace store."""

    def create(
        self,
        task_type: str,
        user_input: str = "",
        tags: list[str] | None = None,
        trace_id: str = "",
    ) -> Trace:
        trace_id = trace_id or f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        trace = Trace(
            trace_id=trace_id,
            task_type=task_type,
            user_input=user_input,
            tags=tags or [],
        )
        return trace

    async def log_step(
        self,
        trace_id: str,
        step_name: str,
        tool_name: str | None = None,
        reasoning_summary: str = "",
        input_summary: str = "",
        output_summary: str = "",
        status: str = "success",
        error_message: str = "",
    ) -> dict:
        """Log a step to database."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        step = {
            "step_name": step_name,
            "tool_name": tool_name or step_name,
            "reasoning_summary": reasoning_summary,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "status": status,
            "started_at": now,
            "ended_at": now,
            "error_message": error_message,
        }

        try:
            async with async_session() as session:
                db_step = TaskStep(
                    trace_id=trace_id,
                    step_name=step_name,
                    tool_name=tool_name or step_name,
                    reasoning_summary=reasoning_summary,
                    input_summary=input_summary,
                    output_summary=output_summary,
                    status=status,
                    started_at=now,
                    ended_at=now,
                    error_message=error_message,
                )
                session.add(db_step)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to persist step {step_name}: {e}")

        return step

    async def complete(
        self,
        trace_id: str,
        status: str = "success",
        error_message: str = "",
        trace: Trace | None = None,
    ) -> Trace | None:
        """Complete a trace and persist to database."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if trace:
            trace.status = status
            trace.ended_at = now
            trace.error_message = error_message
            if trace.started_at:
                try:
                    start = datetime.strptime(trace.started_at, "%Y-%m-%d %H:%M:%S")
                    end = datetime.strptime(trace.ended_at, "%Y-%m-%d %H:%M:%S")
                    trace.duration_ms = int((end - start).total_seconds() * 1000)
                except (ValueError, TypeError):
                    pass

            try:
                async with async_session() as session:
                    existing = await session.execute(
                        select(Task).where(Task.trace_id == trace_id)
                    )
                    task = existing.scalar_one_or_none()

                    if task:
                        task.status = status
                        task.ended_at = now
                        task.duration_ms = trace.duration_ms
                        task.error_message = error_message
                    else:
                        task = Task(
                            trace_id=trace_id,
                            task_type=trace.task_type,
                            user_input=trace.user_input,
                            status=status,
                            started_at=trace.started_at,
                            ended_at=now,
                            duration_ms=trace.duration_ms,
                            error_message=error_message,
                        )
                        task.set_tags(trace.tags)
                        session.add(task)

                    await session.commit()
            except Exception as e:
                logger.error(f"Failed to persist trace {trace_id}: {e}")

        return trace

    async def get(self, trace_id: str) -> dict | None:
        """Get a trace by ID with all its steps."""
        try:
            async with async_session() as session:
                task = await session.execute(
                    select(Task).where(Task.trace_id == trace_id)
                )
                task = task.scalar_one_or_none()
                if not task:
                    return None

                steps_result = await session.execute(
                    select(TaskStep)
                    .where(TaskStep.trace_id == trace_id)
                    .order_by(TaskStep.id)
                )
                steps = steps_result.scalars().all()

                return {
                    "trace_id": task.trace_id,
                    "task_type": task.task_type,
                    "user_input": task.user_input or "",
                    "summary": task.summary or "",
                    "tags": task.get_tags(),
                    "status": task.status,
                    "started_at": task.started_at,
                    "ended_at": task.ended_at,
                    "duration_ms": task.duration_ms or 0,
                    "error_message": task.error_message or "",
                    "steps": [
                        {
                            "step_name": s.step_name,
                            "tool_name": s.tool_name,
                            "reasoning_summary": s.reasoning_summary or "",
                            "input_summary": s.input_summary or "",
                            "output_summary": s.output_summary or "",
                            "status": s.status,
                            "started_at": s.started_at,
                            "ended_at": s.ended_at,
                            "duration_ms": s.duration_ms or 0,
                            "error_message": s.error_message or "",
                        }
                        for s in steps
                    ],
                }

        except Exception as e:
            logger.error(f"Failed to get trace {trace_id}: {e}")
            return None

    async def query(
        self,
        keyword: str = "",
        task_type: str = "",
        status: str = "",
        tag: str = "",
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Query traces from database."""
        try:
            async with async_session() as session:
                query = select(Task)

                if keyword:
                    kw = f"%{keyword}%"
                    query = query.where(
                        Task.user_input.ilike(kw) | Task.summary.ilike(kw)
                    )
                if task_type:
                    query = query.where(Task.task_type == task_type)
                if status:
                    query = query.where(Task.status == status)
                if tag:
                    query = query.where(Task.tags.ilike(f"%{tag}%"))

                count_query = select(func.count()).select_from(query.subquery())
                total = (await session.execute(count_query)).scalar() or 0

                offset = (page - 1) * page_size
                query = query.order_by(Task.started_at.desc()).offset(offset).limit(page_size)
                result = await session.execute(query)
                tasks = result.scalars().all()

                traces = []
                for task in tasks:
                    # Get step count
                    steps_count = await session.execute(
                        select(func.count())
                        .select_from(TaskStep)
                        .where(TaskStep.trace_id == task.trace_id)
                    )
                    step_count = steps_count.scalar() or 0

                    traces.append({
                        "trace_id": task.trace_id,
                        "task_type": task.task_type,
                        "user_input": task.user_input or "",
                        "summary": task.summary or "",
                        "tags": task.get_tags(),
                        "status": task.status,
                        "started_at": task.started_at,
                        "ended_at": task.ended_at,
                        "duration_ms": task.duration_ms or 0,
                        "error_message": task.error_message or "",
                        "steps": [],
                        "step_count": step_count,
                    })

                return {"total": total, "traces": traces}

        except Exception as e:
            logger.error(f"Failed to query traces: {e}")
            return {"total": 0, "traces": []}
