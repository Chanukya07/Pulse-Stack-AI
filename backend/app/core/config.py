"""PulseStack AI — Application Configuration."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ─────────────────────────────────────────
    APP_NAME: str = "PulseStack AI"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ── Security ────────────────────────────────────────────
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # ── Database ────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://pulsestack:pulsestack_dev@localhost:5432/pulsestack"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # ── Elasticsearch ───────────────────────────────────────
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ES_LOG_INDEX: str = "pulsestack-logs"
    ES_LOG_INDEX_PATTERN: str = "pulsestack-logs-*"

    # ── Redis ───────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ── Kafka ───────────────────────────────────────────────
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_LOG_TOPIC: str = "logs.raw"
    KAFKA_ALERT_TOPIC: str = "alerts.new"
    KAFKA_CONSUMER_GROUP: str = "pulsestack-backend"

    # ── AI ──────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEFAULT_LLM_PROVIDER: Literal["openai", "ollama", "openrouter"] = "openai"
    DEFAULT_LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
