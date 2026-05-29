from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite+aiosqlite:///./data/library.db"
    paper_library_dir: str = "./data/paper_library"

    llm_provider: str = ""  # openai, deepseek, qwen, openai-compatible
    llm_api_key: str = ""
    llm_model: str = ""
    llm_base_url: str = ""  # override auto-detected base URL
    embedding_model: str = ""  # for embedding/rerank, defaults to text-embedding-3-small

    smtp_host: str = ""
    smtp_port: str = ""
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""

    feishu_default_webhook: str = ""

    use_react_agent: bool = False  # Enable ReAct Agent for chat routing
    langgraph_checkpoint_db: str = "./data/langgraph_checkpoints.db"

    # Redis cache (optional, all features work without it)
    redis_url: str = ""  # e.g. "redis://localhost:6379/0"; empty = disabled
    redis_ttl_search_min: int = 30  # min minutes for arXiv search cache TTL
    redis_ttl_search_max: int = 360  # max minutes (6 hours)
    redis_ttl_embedding_days: int = 7
    redis_ttl_rerank_min: int = 30
    redis_ttl_rerank_max: int = 120
    redis_ttl_workflow_hours: int = 24

    class Config:
        env_file = ".env"


settings = Settings()
