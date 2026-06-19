"""Application configuration, sourced from environment (12-factor).

All settings are read from `SCP_`-prefixed env vars (or a local `.env`). No
secrets live in the repo (see 16-security-model).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the Memory Core service."""

    model_config = SettingsConfigDict(env_prefix="SCP_", env_file=".env", extra="ignore")

    # Relational store: SQLite for the MVP, PostgreSQL URL for scale (ADR-005/006).
    database_url: str = "sqlite:///./scp_memory.db"
    log_level: str = "INFO"
    service_name: str = "scp-memory-core"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
