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

    class Config:
        env_file = ".env"


settings = Settings()
