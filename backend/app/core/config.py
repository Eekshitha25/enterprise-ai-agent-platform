"""
Centralized application configuration, loaded from environment variables (.env).
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_env: str = "development"
    log_level: str = "INFO"

    # LLM
    model_provider: str = "ollama"  # ollama (free/local) | anthropic | openai
    chat_model: str = "llama3.1"
    ollama_base_url: str = "http://host.docker.internal:11434"

    embedding_provider: str = "local"  # local (free, sentence-transformers) | openai
    embedding_model: str = "text-embedding-3-large"

    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Postgres
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "agent_platform"
    postgres_user: str = "agent_admin"
    postgres_password: str = "change_me"

    # Qdrant
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection: str = "enterprise_knowledge"

    # AWS
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    use_mock_aws_tool: bool = True

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
