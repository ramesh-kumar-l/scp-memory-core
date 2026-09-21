"""PostgreSQL integration tests (scale-path parity).

Skipped unless ``SCP_TEST_POSTGRES_URL`` points at a reachable PostgreSQL — set in
CI (services: postgres). Proves the same code paths that run on SQLite work on
Postgres, and that the ``tsvector`` keyword backend matches and ranks via its GIN
index. Marked ``postgres`` so it is opt-in.
"""

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import scp_memory.models  # noqa: F401  (register tables)
from scp_memory.db.base import Base
from scp_memory.models.enums import MemoryType
from scp_memory.schemas.memory import MemoryCreate
from scp_memory.services import memory_service
from scp_memory.services.tsvector_backend import TsvectorBackend

pytestmark = pytest.mark.postgres

POSTGRES_URL = os.getenv("SCP_TEST_POSTGRES_URL")


@pytest.fixture
def pg_db():
    if not POSTGRES_URL:
        pytest.skip("SCP_TEST_POSTGRES_URL not set")
    engine = create_engine(POSTGRES_URL, future=True, pool_pre_ping=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False, future=True)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


def _seed(db):
    contents = [
        "the capital of france is paris",
        "python is a popular programming language",
        "the nightly database backup failed",
    ]
    return [
        memory_service.create(
            db, MemoryCreate(content=c, namespace="pg", type=MemoryType.fact), actor="test"
        )
        for c in contents
    ]


def test_crud_roundtrip_on_postgres(pg_db):
    created = memory_service.create(
        pg_db,
        MemoryCreate(content="hello postgres", namespace="pg", type=MemoryType.fact),
        actor="test",
    )
    fetched = memory_service.get(pg_db, created.id, namespace="pg")
    assert fetched.content == "hello postgres"
    rows, total = memory_service.list_memories(pg_db, namespace="pg")
    assert total == 1 and rows[0].id == created.id


def test_tsvector_backend_matches_and_ranks(pg_db):
    memories = _seed(pg_db)
    backend = TsvectorBackend()
    scores = backend.scores(
        db=pg_db, query="capital of france", namespace="pg", type_=None, candidates=memories
    )
    assert scores
    assert max(scores, key=scores.get) == memories[0].id
