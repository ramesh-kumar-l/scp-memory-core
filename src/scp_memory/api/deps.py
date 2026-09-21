"""FastAPI dependencies: DB session and request actor.

Tests override `get_db` to point at an isolated engine.
"""

from collections.abc import Iterator

from fastapi import Header
from sqlalchemy.orm import Session

from scp_memory.db.session import SessionLocal


def get_db() -> Iterator[Session]:
    """Yield a request-scoped session and ensure it is closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_actor(x_actor: str | None = Header(default=None)) -> str:
    """Identify the caller for audit purposes (placeholder for Phase-4 authz)."""
    return x_actor or "anonymous"
