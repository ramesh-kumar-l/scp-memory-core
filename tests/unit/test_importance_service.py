"""Importance is set at create and refreshed by access (frequency)."""

from scp_memory.schemas.memory import MemoryCreate
from scp_memory.services import importance_service, memory_service


def _create(db, *, ns="user:1", content="hello", meta=None):
    return memory_service.create(
        db, MemoryCreate(content=content, namespace=ns, metadata=meta or {}), actor="t"
    )


def test_create_sets_importance(db):
    memory = _create(db)
    assert memory.importance is not None
    assert 0.0 <= memory.importance <= 1.0


def test_access_increments_count_and_raises_importance(db):
    memory = _create(db)
    before = memory.importance
    fetched = memory_service.get(db, memory.id)
    assert fetched.access_count == 1
    assert fetched.importance >= before  # frequency signal added


def test_pinned_metadata_scores_higher_than_plain(db):
    plain = _create(db, content="a")
    pinned = _create(db, content="b", meta={"pinned": True})
    assert pinned.importance > plain.importance


def test_recompute_is_pure_assignment(db):
    memory = _create(db)
    value = importance_service.recompute(memory)
    assert memory.importance == value
