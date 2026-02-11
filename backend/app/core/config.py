import json
from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import AnyHttpUrl, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = ""
    postgres_db: str = "kasperjunge"
    postgres_user: str = "kasperjunge"
    postgres_password: str = "kasperjunge"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    slack_webhook_url: AnyHttpUrl | None = None
    cors_origins: str = "http://localhost:8000"
    rate_limit_enabled: bool = False
    redis_url: str | None = None
    rate_limit_contact: str = "10/minute"
    rate_limit_analytics: str = "120/minute"
    log_level: str = "INFO"
    log_json: bool = True
    log_file_path: str = "./logs/backend.log"
    log_file_max_bytes: int = 10 * 1024 * 1024
    log_file_backup_count: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @field_validator("slack_webhook_url", mode="before")
    @classmethod
    def empty_slack_url_is_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: object) -> object:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        return value

    @model_validator(mode="after")
    def ensure_database_url(self) -> "Settings":
        if self.database_url:
            return self

        self.database_url = (
            "postgresql+psycopg://"
            f"{quote_plus(self.postgres_user)}:{quote_plus(self.postgres_password)}@"
            f"{self.postgres_host}:{self.postgres_port}/{quote_plus(self.postgres_db)}"
        )
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        stripped = self.cors_origins.strip()
        if not stripped:
            return []

        if stripped.startswith("["):
            parsed = json.loads(stripped)
            return [str(origin).strip() for origin in parsed if str(origin).strip()]

        return [origin.strip() for origin in stripped.split(",") if origin.strip()]

    @property
    def docs_enabled(self) -> bool:
        return self.app_env.lower() not in {"staging", "production", "prod"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
