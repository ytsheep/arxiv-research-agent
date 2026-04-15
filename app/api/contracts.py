from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from app.models import DeliveryResult, Paper


class SearchRequest(BaseModel):
    query: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    focus: str = Field(..., description="Research focus used by the agent.")
    top_k: int = Field(default=5, ge=1, le=20)
    max_results: int = Field(default=50, ge=1, le=100)
    api_key: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    focus: str
    markdown: str
    papers: List[Paper]
    tool_trace: List[str]


class RecipientPayload(BaseModel):
    channel: Literal["email", "feishu"]
    target: str = Field(..., min_length=1)
    enabled: bool = True


class SubscriptionCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    query: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    focus: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    max_results: int = Field(default=50, ge=1, le=100)
    schedule_hour: int = Field(default=8, ge=0, le=23)
    schedule_minute: int = Field(default=0, ge=0, le=59)
    timezone: str = "Asia/Shanghai"
    dedupe_days: int = Field(default=1, ge=1, le=30)
    enabled: bool = True
    recipients: List[RecipientPayload] = Field(default_factory=list)


class SubscriptionUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    query: Optional[str] = None
    keywords: Optional[List[str]] = None
    focus: Optional[str] = Field(default=None, min_length=1)
    top_k: Optional[int] = Field(default=None, ge=1, le=20)
    max_results: Optional[int] = Field(default=None, ge=1, le=100)
    schedule_hour: Optional[int] = Field(default=None, ge=0, le=23)
    schedule_minute: Optional[int] = Field(default=None, ge=0, le=59)
    timezone: Optional[str] = None
    dedupe_days: Optional[int] = Field(default=None, ge=1, le=30)
    enabled: Optional[bool] = None
    recipients: Optional[List[RecipientPayload]] = None


class SubscriptionRecipientResponse(BaseModel):
    id: int
    channel: str
    target: str
    enabled: bool


class SubscriptionResponse(BaseModel):
    id: int
    name: str
    query: Optional[str]
    effective_query: str
    keywords: List[str]
    focus: str
    top_k: int
    max_results: int
    schedule_hour: int
    schedule_minute: int
    timezone: str
    dedupe_days: int
    enabled: bool
    recipients: List[SubscriptionRecipientResponse]
    created_at: datetime
    updated_at: datetime


class DigestRunResponse(BaseModel):
    id: int
    subscription_id: int
    trigger_mode: str
    scheduled_for_date: Optional[date]
    status: str
    papers_count: int
    error_message: Optional[str]
    started_at: datetime
    finished_at: Optional[datetime]


class DigestTriggerRequest(BaseModel):
    notify: bool = True
    api_key: Optional[str] = None


class DigestTriggerResponse(BaseModel):
    subscription_id: int
    subscription_name: str
    query: str
    focus: str
    papers_count: int
    notified_channels: List[str]
    generated_at: datetime
    delivery_results: List[DeliveryResult]
