from pydantic import BaseModel


class SubscriptionCreate(BaseModel):
    name: str
    topics: list[str]
    categories: list[str] = []
    candidate_k: int = 20
    top_n: int = 2
    cron_expr: str = "0 8 * * *"
    timezone: str = "Asia/Shanghai"
    email_enabled: bool = False
    email_to: str = ""
    feishu_enabled: bool = False
    feishu_webhook_ref: str = ""
    auto_parse_full_text: bool = False


class SubscriptionUpdate(BaseModel):
    name: str | None = None
    topics: list[str] | None = None
    categories: list[str] | None = None
    candidate_k: int | None = None
    top_n: int | None = None
    cron_expr: str | None = None
    timezone: str | None = None
    email_enabled: bool | None = None
    email_to: str | None = None
    feishu_enabled: bool | None = None
    feishu_webhook_ref: str | None = None
    auto_parse_full_text: bool | None = None
    enabled: bool | None = None


class SubscriptionItem(BaseModel):
    id: int
    name: str
    topics: list[str]
    categories: list[str] = []
    candidate_k: int = 20
    top_n: int = 2
    cron_expr: str = ""
    timezone: str = ""
    email_enabled: bool = False
    email_to: str = ""
    feishu_enabled: bool = False
    feishu_webhook_ref: str = ""
    auto_parse_full_text: bool = False
    enabled: bool = True
    created_at: str = ""
    updated_at: str = ""


class SubscriptionListResponse(BaseModel):
    success: bool = True
    subscriptions: list[SubscriptionItem] = []
