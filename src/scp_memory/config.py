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

    # Memory intelligence knobs (Phase 2). Operational thresholds for the batch
    # decay/dedup passes; scoring weights live in intelligence.scoring.ScoringConfig.
    decay_threshold: float = 0.25  # importance below this → decayed
    dedup_similarity_threshold: float = 0.85  # Jaccard at/above this → duplicate

    # Hybrid retrieval (Phase 3). Vector backend: "bruteforce" (default, in-process,
    # zero-infra) or "qdrant" (scale path; needs the [vector] extra + a running
    # Qdrant). Algorithmic knobs (dims, weights, k) live in retrieval.config.
    vector_backend: str = "bruteforce"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "scp_memories"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
