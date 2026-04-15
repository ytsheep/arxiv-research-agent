from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "arXiv Research Agent"
    environment: str = "development"
    timezone: str = "Asia/Shanghai"
    log_level: str = "INFO"

    dashscope_api_key: str = Field(default="", alias="DASHSCOPE_API_KEY")
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    llm_model: str = "qwen-plus"

    database_url: str = "sqlite:///./data/arxiv_agent.db"
    request_timeout_seconds: int = 20

    digest_enabled: bool = True
    scheduler_scan_interval_minutes: int = 1
    scheduler_max_workers: int = 4

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    email_from: str = ""

    def ensure_directories(self) -> None:
        if self.database_url.startswith("sqlite:///"):
            sqlite_path = BASE_DIR / self.database_url.replace("sqlite:///", "", 1)
            sqlite_path.parent.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
