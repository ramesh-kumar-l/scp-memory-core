"""Decay transitions stale, low-importance memories to `decayed`."""

from datetime import timedelta

from scp_memory.models.enums import MemoryState
from scp_memory.schemas.memory import MemoryCreate
from scp_memory.services import decay_service, memory_service
from scp_memory.utils.time import utcnow


def _create(db, content="some fact", ns="user:1"):
    return memory_service.create(db, MemoryCreate(content=content, namespace=ns), actor="t")


def test_fresh_memory_is_not_decayed(db):
    memory = _create(db)
    scanned, decayed = decay_service.run(db, namespace="user:1")
    assert scanned == 1
    assert decayed == []
    assert memory.state == MemoryState.active.value


def test_old_memory_decays_and_is_audited(db):
    memory = _create(db)
    far_future = utcnow() + timedelta(days=3650)
    scanned, decayed = decay_service.run(db, namespace="user:1", now=far_future)
    assert decayed == [memory.id]
    db.refresh(memory)
    assert memory.state == MemoryState.decayed.value

    from scp_memory.services import audit_service

    events, _ = audit_service.list_for_memory(db, memory.id)
    assert any(e.action == "decay" for e in events)


def test_decayed_memory_excluded_from_default_list(db):
    memory = _create(db)
    decay_service.run(db, namespace="user:1", now=utcnow() + timedelta(days=3650))
    items, total = memory_service.list_memories(db, namespace="user:1")
    assert memory.id not in {m.id for m in items}
    assert total == 0
    # ...but reachable via explicit state filter.
    items, total = memory_service.list_memories(db, namespace="user:1", state="decayed")
    assert total == 1
