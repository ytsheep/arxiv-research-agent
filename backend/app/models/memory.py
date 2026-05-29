from sqlalchemy import Column, Float, Integer, String, Text
from app.db.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String, default="chat")
    group_id = Column(String, index=True)
    tool_call_id = Column(String)
    tool_name = Column(String)
    metadata_json = Column(Text)
    token_estimate = Column(Integer, default=0)
    created_at = Column(String)


class SemanticMemory(Base):
    __tablename__ = "semantic_memories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, index=True)
    source_type = Column(String, index=True, nullable=False)
    source_id = Column(String, index=True, nullable=False)
    title = Column(String)
    content = Column(Text, nullable=False)
    metadata_json = Column(Text)
    embedding_json = Column(Text)
    importance = Column(Float, default=0.5)
    created_at = Column(String)
    updated_at = Column(String)
