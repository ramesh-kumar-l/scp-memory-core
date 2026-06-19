"""Decay service — age out low-importance memories (12-memory-model).

A batch maintenance pass over a namespace: recompute importance for every active
memory and transition those below the configured threshold to `decayed`. Decayed
memories are retained (audit + recovery) but excluded from the default active set.
Every transition emits an audit event in the same transaction.
"""

import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from scp_memory.config import get_settings
from scp_memory.metrics import MEMORIES_DECAYED
from scp_memory.models.enums import AuditAction, MemoryState
from scp_memory.models.memory import Memory
from scp_memory.services import audit_service, importance_service

logger = logging.getLogger("scp_memory.decay")


def run(
    db: Session,
    *,
    namespace: str,
    threshold: float | None = None,
    now: datetime | None = None,
) -> tuple[int, list[str]]:
    """Recompute importance for active memories; decay those below `threshold`.

    Returns ``(scanned, decayed_ids)``. ``now`` is injectable for testing.
    """
    if threshold is None:
        threshold = get_settings().decay_threshold

    rows = list(
        db.scalars(
            select(Memory).where(
                Memory.namespace == namespace,
                Memory.state == MemoryState.active.value,
            )
        )
    )

    decayed_ids: list[str] = []
    for memory in rows:
        importance = importance_service.recompute(memory, now=now)
        if importance < threshold:
            memory.state = MemoryState.decayed.value
            audit_service.record(
                db,
                memory_id=memory.id,
                action=AuditAction.decay,
                actor="system",
                diff={
                    "importance": importance,
                    "threshold": threshold,
                    "state": {"before": "active", "after": "decayed"},
                },
            )
            MEMORIES_DECAYED.inc()
            decayed_ids.append(memory.id)

    db.commit()
    logger.info(
        "decay_pass",
        extra={"namespace": namespace, "scanned": len(rows), "decayed": len(decayed_ids)},
    )
    return len(rows), decayed_ids
