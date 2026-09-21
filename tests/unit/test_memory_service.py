"""Unit tests for the memory service (CRUD, namespacing, invariants)."""

import pytest

from scp_memory.models.enums import MemoryState, MemoryType
from scp_memory.schemas.memory import MemoryCreate, MemoryUpdate
from scp_memory.services import memory_service
from scp_memory.services.errors import NotFoundError


def _create(db, *, ns="user:1", content="prefers dark mode", actor="tester"):
    return memory_service.create(
        db, MemoryCreate(content=content, namespace=ns, type=MemoryType.preference), actor=actor
    )


def test_create_sets_active_state_and_provenance(db):
    memory = _create(db)
    assert memory.id.startswith("mem_")
    assert memory.state == MemoryState.active.value
    assert memory.provenance is not None
    assert memory.provenance.actor == "tester"


def test_get_touches_last_accessed(db):
    memory = _create(db)
    assert memory.last_accessed_at is None
    fetched = memory_service.get(db, memory.id)
    assert fetched.last_accessed_at is not None


def test_namespace_isolation_hides_other_tenants(db):
    memory = _create(db, ns="user:1")
    with pytest.raises(NotFoundError):
        memory_service.get(db, memory.id, namespace="user:2")


def test_update_only_audits_changed_fields(db):
    memory = _create(db, content="old")
    updated = memory_service.update(db, memory.id, MemoryUpdate(content="new"), actor="tester")
    assert updated.content == "new"
    events, _ = _audit(db, memory.id)
    update_events = [e for e in events if e.action == "update"]
    assert len(update_events) == 1
    assert update_events[0].diff["changes"]["content"]["after"] == "new"


def test_update_noop_emits_no_audit(db):
    memory = _create(db, content="same")
    memory_service.update(db, memory.id, MemoryUpdate(content="same"), actor="tester")
    events, _ = _audit(db, memory.id)
    assert [e.action for e in events] == ["create"]


def test_soft_delete_marks_state_and_hides_from_get(db):
    memory = _create(db)
    memory_service.delete(db, memory.id, actor="tester")
    with pytest.raises(NotFoundError):
        memory_service.get(db, memory.id)


def test_hard_delete_removes_row_but_keeps_audit(db):
    memory = _create(db)
    memory_service.delete(db, memory.id, actor="tester", hard=True)
    events, total = _audit(db, memory.id)
    assert total >= 2  # create + delete
    assert any(e.action == "delete" and e.diff.get("hard") for e in events)


def test_list_excludes_deleted_by_default(db):
    keep = _create(db, content="keep")
    gone = _create(db, content="gone")
    memory_service.delete(db, gone.id, actor="tester")
    items, total = memory_service.list_memories(db, namespace="user:1")
    ids = {m.id for m in items}
    assert keep.id in ids
    assert gone.id not in ids
    assert total == 1


def _audit(db, memory_id):
    from scp_memory.services import audit_service

    return audit_service.list_for_memory(db, memory_id)
