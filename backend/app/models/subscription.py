from sqlalchemy import Column, Integer, String, Text, DateTime
from app.db.database import Base
import json


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    topics = Column(Text, nullable=False)  # JSON string
    categories = Column(Text)  # JSON string
    candidate_k = Column(Integer, default=20)
    top_n = Column(Integer, default=2)
    cron_expr = Column(String, nullable=False)
    timezone = Column(String)
    email_enabled = Column(Integer, default=0)
    email_to = Column(Text)
    feishu_enabled = Column(Integer, default=0)
    feishu_webhook_ref = Column(Text)
    auto_parse_full_text = Column(Integer, default=0)
    enabled = Column(Integer, default=1)
    created_at = Column(String)
    updated_at = Column(String)

    def get_topics(self) -> list[str]:
        return json.loads(self.topics) if self.topics else []

    def set_topics(self, topics: list[str]):
        self.topics = json.dumps(topics, ensure_ascii=False)

    def get_categories_list(self) -> list[str]:
        return json.loads(self.categories) if self.categories else []

    def set_categories_list(self, categories: list[str]):
        self.categories = json.dumps(categories, ensure_ascii=False)


class SubscriptionRun(Base):
    __tablename__ = "subscription_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subscription_id = Column(Integer, nullable=False)
    run_date = Column(String)
    selected_papers = Column(Text)  # JSON string
    sent_email = Column(Integer, default=0)
    sent_feishu = Column(Integer, default=0)
    status = Column(String)
    error_message = Column(Text)
    trace_id = Column(String)
    created_at = Column(String)
