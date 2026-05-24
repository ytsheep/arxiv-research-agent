from sqlalchemy import Column, Integer, String, Text, DateTime
from app.db.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String, unique=True, nullable=False)
    task_type = Column(String, nullable=False)
    user_input = Column(Text)
    summary = Column(Text)
    tags = Column(Text)  # comma-separated tags
    status = Column(String)
    started_at = Column(String)
    ended_at = Column(String)
    duration_ms = Column(Integer)
    error_message = Column(Text)

    def get_tags(self) -> list[str]:
        return self.tags.split(",") if self.tags else []

    def set_tags(self, tags: list[str]):
        self.tags = ",".join(tags)


class TaskStep(Base):
    __tablename__ = "task_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String, nullable=False)
    step_name = Column(String, nullable=False)
    tool_name = Column(String)
    reasoning_summary = Column(Text)
    input_summary = Column(Text)
    output_summary = Column(Text)
    status = Column(String)
    started_at = Column(String)
    ended_at = Column(String)
    duration_ms = Column(Integer)
    error_message = Column(Text)
