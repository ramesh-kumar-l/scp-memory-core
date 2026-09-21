"""Engine and session-factory construction.

Storage is pluggable (09 design tenet): the same code targets SQLite (MVP) or
PostgreSQL (scale) purely by `database_url`. SQLite gets sane pragmas for
concurrency and referential integrity.
"""

import sqlite3

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


@event.listens_for(Engine, "connect")
def _set_sqlite_pragmas(dbapi_connection, _connection_record) -> None:
    """Enforce foreign keys and enable WAL for SQLite connections."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


def make_engine(database_url: str) -> Engine:
    """Create a configured Engine for the given URL."""
    connect_args: dict = {}
    if database_url.startswith("sqlite"):
        # FastAPI runs sync routes in a threadpool; allow cross-thread use.
        connect_args["check_same_thread"] = False
    return create_engine(
        database_url,
        future=True,
        echo=False,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a session factory bound to the engine."""
    return sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
        future=True,
    )
