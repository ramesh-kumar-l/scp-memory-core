"""Audit service — append-only event emission (16-security-model).

`record` adds an event to the session but does NOT commit: the caller commits the
mutation and its audit event together, so they are atomic.
"""

import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from scp_memory.metrics import AUDIT_EVENTS
from scp_memory.models.audit import AuditEvent
from scp_memory.models.enums import AuditAction

logger = logging.getLogger("scp_memory.audit")


def record(
    db: Session,
    *,
    memory_id: str,
    action: AuditAction,
    actor: str,
    diff: dict | None = None,
) -> AuditEvent:
    """Append an audit event for a memory mutation."""
    event = AuditEvent(
        memory_id=memory_id,
        action=action.value,
        actor=actor,
        diff=diff or {},
    )
    db.add(event)
    AUDIT_EVENTS.labels(action=action.value).inc()
    # Operational log mirrors audit, but carries no memory content (privacy).
    logger.info(
        "audit",
        extra={"memory_id": memory_id, "action": action.value, "actor": actor},
    )
    return event


def list_for_memory(db: Session, memory_id: str) -> tuple[list[AuditEvent], int]:
    """Return all audit events for a memory, newest first, with a total count."""
    total = db.scalar(
        select(func.count()).select_from(AuditEvent).where(AuditEvent.memory_id == memory_id)
    )
    rows = list(
        db.scalars(
            select(AuditEvent)
            .where(AuditEvent.memory_id == memory_id)
            .order_by(AuditEvent.timestamp.desc(), AuditEvent.id.desc())
        )
    )
    return rows, int(total or 0)
