"""Unit tests for the audit service (append-only, ordering)."""

from scp_memory.models.enums import AuditAction
from scp_memory.services import audit_service


def test_record_requires_commit_to_persist(db):
    audit_service.record(db, memory_id="mem_x", action=AuditAction.create, actor="a")
    db.commit()
    events, total = audit_service.list_for_memory(db, "mem_x")
    assert total == 1
    assert events[0].action == "create"
    assert events[0].actor == "a"


def test_events_returned_newest_first(db):
    for action in (AuditAction.create, AuditAction.update, AuditAction.delete):
        audit_service.record(db, memory_id="mem_y", action=action, actor="a")
        db.commit()
    events, total = audit_service.list_for_memory(db, "mem_y")
    assert total == 3
    assert events[0].action == "delete"
    assert events[-1].action == "create"
