"""Process-wide engine/session factory and schema bootstrap.

Tests build their own isolated engines and override the API dependency, so they
never touch this module-level engine.
"""

from scp_memory.config import get_settings
from scp_memory.db.base import Base
from scp_memory.db.engine import make_engine, make_session_factory

_settings = get_settings()

engine = make_engine(_settings.database_url)
SessionLocal = make_session_factory(engine)


def init_db() -> None:
    """Create all tables on the process-wide engine (idempotent, MVP)."""
    import scp_memory.models  # noqa: F401  (register tables on Base.metadata)

    Base.metadata.create_all(bind=engine)
