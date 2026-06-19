"""Memory service — CRUD with namespacing and atomic audit (12-memory-model).

Invariants enforced here:
- Every mutation emits an AuditEvent in the same transaction.
- Provenance is always recorded and never lost.
- The relational record is the source of truth.
- Namespace scoping isolates tenants; mismatches read as "not found" (no leak).
"""

import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from scp_memory.metrics import MEMORIES_CREATED, MEMORIES_DELETED, MEMORIES_UPDATED
from scp_memory.models.enums import AuditAction, MemoryState
from scp_memory.models.memory import Memory
from scp_memory.models.provenance import Provenance
from scp_memory.schemas.memory import MemoryCreate, MemoryUpdate
from scp_memory.services import audit_service
from scp_memory.services.errors import NotFoundError
from scp_memory.utils.time import utcnow

logger = logging.getLogger("scp_memory.memory")


def _snapshot(memory: Memory) -> dict:
    """A content snapshot for audit diffs (no timestamps; IDs/metadata only)."""
    return {
        "content": memory.content,
        "type": memory.type,
        "state": memory.state,
        "namespace": memory.namespace,
        "metadata": memory.meta,
    }


def _get(db: Session, memory_id: str, namespace: str | None, *, include_deleted: bool) -> Memory:
    memory = db.get(Memory, memory_id)
    if memory is None:
        raise NotFoundError(f"memory '{memory_id}' not found")
    if namespace is not None and memory.namespace != namespace:
        raise NotFoundError(f"memory '{memory_id}' not found")
    if not include_deleted and memory.state == MemoryState.deleted.value:
        raise NotFoundError(f"memory '{memory_id}' not found")
    return memory


def create(db: Session, data: MemoryCreate, *, actor: str) -> Memory:
    """Create an active memory with provenance and a create audit event."""
    memory = Memory(
        content=data.content,
        type=data.type.value,
        state=MemoryState.active.value,
        namespace=data.namespace,
        meta=data.metadata,
    )
    memory.provenance = Provenance(
        source=data.source or "user",
        actor=actor,
        derivation={"kind": "raw"},
    )
    db.add(memory)
    db.flush()  # assign server-generated id
    audit_service.record(
        db,
        memory_id=memory.id,
        action=AuditAction.create,
        actor=actor,
        diff={"after": _snapshot(memory)},
    )
    db.commit()
    db.refresh(memory)
    MEMORIES_CREATED.inc()
    return memory


def get(db: Session, memory_id: str, *, namespace: str | None = None, touch: bool = True) -> Memory:
    """Fetch a non-deleted memory; updates `last_accessed_at` when `touch`."""
    memory = _get(db, memory_id, namespace, include_deleted=False)
    if touch:
        memory.last_accessed_at = utcnow()
        db.commit()
        db.refresh(memory)
    return memory


def update(
    db: Session, memory_id: str, data: MemoryUpdate, *, actor: str, namespace: str | None = None
) -> Memory:
    """Apply a partial update; audits only the fields that actually changed."""
    memory = _get(db, memory_id, namespace, include_deleted=False)
    changes: dict[str, dict] = {}
    if data.content is not None and data.content != memory.content:
        changes["content"] = {"before": memory.content, "after": data.content}
        memory.content = data.content
    if data.type is not None and data.type.value != memory.type:
        changes["type"] = {"before": memory.type, "after": data.type.value}
        memory.type = data.type.value
    if data.metadata is not None and data.metadata != memory.meta:
        changes["metadata"] = {"before": memory.meta, "after": data.metadata}
        memory.meta = data.metadata

    if not changes:
        return memory  # no-op: nothing to audit

    audit_service.record(
        db,
        memory_id=memory.id,
        action=AuditAction.update,
        actor=actor,
        diff={"changes": changes},
    )
    db.commit()
    db.refresh(memory)
    MEMORIES_UPDATED.inc()
    return memory


def delete(
    db: Session, memory_id: str, *, actor: str, hard: bool = False, namespace: str | None = None
) -> None:
    """Governed delete: soft by default (state=deleted), hard on request.

    The audit event is recorded either way and survives a hard delete.
    """
    memory = _get(db, memory_id, namespace, include_deleted=True)
    if hard:
        audit_service.record(
            db,
            memory_id=memory.id,
            action=AuditAction.delete,
            actor=actor,
            diff={"hard": True, "before": _snapshot(memory)},
        )
        db.delete(memory)
        db.commit()
        MEMORIES_DELETED.labels(mode="hard").inc()
        return

    if memory.state == MemoryState.deleted.value:
        return  # already soft-deleted; idempotent
    memory.state = MemoryState.deleted.value
    audit_service.record(
        db,
        memory_id=memory.id,
        action=AuditAction.delete,
        actor=actor,
        diff={"hard": False, "state": {"before": "active", "after": "deleted"}},
    )
    db.commit()
    MEMORIES_DELETED.labels(mode="soft").inc()


def list_memories(
    db: Session,
    *,
    namespace: str,
    type_: str | None = None,
    state: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Memory], int]:
    """List memories in a namespace. Excludes deleted unless `state` is given."""
    filters = [Memory.namespace == namespace]
    if state is not None:
        filters.append(Memory.state == state)
    else:
        filters.append(Memory.state != MemoryState.deleted.value)
    if type_ is not None:
        filters.append(Memory.type == type_)

    total = db.scalar(select(func.count()).select_from(Memory).where(*filters))
    rows = list(
        db.scalars(
            select(Memory)
            .where(*filters)
            .order_by(Memory.created_at.desc(), Memory.id.desc())
            .limit(limit)
            .offset(offset)
        )
    )
    return rows, int(total or 0)
