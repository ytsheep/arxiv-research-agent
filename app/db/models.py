from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    query: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    focus: Mapped[str] = mapped_column(Text, nullable=False)
    top_k: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    max_results: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    schedule_hour: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    schedule_minute: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Shanghai", nullable=False)
    dedupe_days: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    keywords: Mapped[List["SubscriptionKeyword"]] = relationship(
        back_populates="subscription",
        cascade="all, delete-orphan",
        order_by="SubscriptionKeyword.sort_order",
    )
    recipients: Mapped[List["SubscriptionRecipient"]] = relationship(
        back_populates="subscription",
        cascade="all, delete-orphan",
        order_by="SubscriptionRecipient.id",
    )
    runs: Mapped[List["DigestRun"]] = relationship(
        back_populates="subscription",
        cascade="all, delete-orphan",
        order_by="DigestRun.started_at.desc()",
    )


class SubscriptionKeyword(Base):
    __tablename__ = "subscription_keywords"
    __table_args__ = (
        UniqueConstraint("subscription_id", "keyword", name="uq_subscription_keyword"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id", ondelete="CASCADE"))
    keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    subscription: Mapped["Subscription"] = relationship(back_populates="keywords")


class SubscriptionRecipient(Base, TimestampMixin):
    __tablename__ = "subscription_recipients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id", ondelete="CASCADE"))
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    target: Mapped[str] = mapped_column(Text, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    subscription: Mapped["Subscription"] = relationship(back_populates="recipients")
    deliveries: Mapped[List["DigestDelivery"]] = relationship(back_populates="recipient")


class DigestRun(Base):
    __tablename__ = "digest_runs"
    __table_args__ = (
        UniqueConstraint("subscription_id", "scheduled_for_date", name="uq_subscription_scheduled_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id", ondelete="CASCADE"))
    trigger_mode: Mapped[str] = mapped_column(String(32), default="manual", nullable=False)
    scheduled_for_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="running", nullable=False)
    papers_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    subscription: Mapped["Subscription"] = relationship(back_populates="runs")
    items: Mapped[List["DigestRunItem"]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="DigestRunItem.id",
    )
    deliveries: Mapped[List["DigestDelivery"]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="DigestDelivery.id",
    )


class DigestRunItem(Base):
    __tablename__ = "digest_run_items"
    __table_args__ = (
        UniqueConstraint("digest_run_id", "paper_id", name="uq_digest_run_item_paper"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    digest_run_id: Mapped[int] = mapped_column(ForeignKey("digest_runs.id", ondelete="CASCADE"))
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id", ondelete="CASCADE"))
    paper_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    entry_url: Mapped[str] = mapped_column(Text, nullable=False)
    published: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    run: Mapped["DigestRun"] = relationship(back_populates="items")


class DigestDelivery(Base):
    __tablename__ = "digest_deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    digest_run_id: Mapped[int] = mapped_column(ForeignKey("digest_runs.id", ondelete="CASCADE"))
    recipient_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("subscription_recipients.id", ondelete="SET NULL"),
        nullable=True,
    )
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    target: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    run: Mapped["DigestRun"] = relationship(back_populates="deliveries")
    recipient: Mapped[Optional["SubscriptionRecipient"]] = relationship(back_populates="deliveries")
