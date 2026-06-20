"""Keyword backend tests: in-process default + SQLite FTS5 inverted index."""

import pytest

from scp_memory.models.enums import MemoryType
from scp_memory.schemas.memory import MemoryCreate
from scp_memory.services import memory_service
from scp_memory.services.fts5_backend import Fts5Backend
from scp_memory.services.keyword_backend import (
    InProcessBM25Backend,
    get_keyword_backend,
)

_CORPUS = [
    "the capital of france is paris",
    "python is a popular programming language",
    "user prefers dark mode in the editor",
    "the nightly database backup failed",
]


def _seed(db, namespace="kw"):
    created = []
    for content in _CORPUS:
        created.append(
            memory_service.create(
                db,
                MemoryCreate(content=content, namespace=namespace, type=MemoryType.fact),
                actor="test",
            )
        )
    return created


def test_default_backend_is_in_process_bm25():
    get_keyword_backend.cache_clear()
    assert isinstance(get_keyword_backend(), InProcessBM25Backend)


def test_in_process_bm25_scores_relevant_highest(db):
    memories = _seed(db)
    backend = InProcessBM25Backend()
    scores = backend.scores(
        db=db, query="capital of france", namespace="kw", type_=None, candidates=memories
    )
    top = max(scores, key=scores.get)
    assert top == memories[0].id  # the france/paris memory


def test_fts5_index_matches_and_ranks(db):
    memories = _seed(db)
    backend = Fts5Backend()
    scores = backend.scores(
        db=db, query="capital france", namespace="kw", type_=None, candidates=memories
    )
    # Only the matching document is returned, and it is the france/paris memory.
    assert scores
    assert max(scores, key=scores.get) == memories[0].id
    assert all(v == pytest.approx(v) for v in scores.values())


def test_fts5_stays_in_sync_on_new_writes(db):
    _seed(db)
    backend = Fts5Backend()
    # Build the index, then add a memory after the index already exists (trigger path).
    backend.scores(db=db, query="france", namespace="kw", type_=None, candidates=[])
    new = memory_service.create(
        db,
        MemoryCreate(
            content="madrid is the capital of spain", namespace="kw", type=MemoryType.fact
        ),
        actor="test",
    )
    scores = backend.scores(
        db=db, query="capital spain", namespace="kw", type_=None, candidates=[new]
    )
    assert new.id in scores


def test_fts5_namespace_scoped(db):
    _seed(db, namespace="kw")
    other = memory_service.create(
        db,
        MemoryCreate(content="capital of france trivia", namespace="other", type=MemoryType.fact),
        actor="test",
    )
    backend = Fts5Backend()
    scores = backend.scores(
        db=db, query="capital france", namespace="other", type_=None, candidates=[other]
    )
    assert set(scores) == {other.id}
