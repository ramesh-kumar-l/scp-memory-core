"""Consolidation service — merge related memories into a summary (12-memory-model).

Takes two or more active source memories, produces a new `summary` memory that
records `derived_from` edges and source IDs in its provenance, and transitions the
sources to `consolidated`. Provenance is never lost.

The summary text is caller-supplied; absent one, a deterministic join is used.
LLM-generated summaries are a later enhancement — the merge graph/provenance is
identical regardless of how the text is produced.
"""

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from scp_memory.metrics import MEMORIES_CONSOLIDATED
from scp_memory.models.enums import AuditAction, MemoryState, MemoryType, RelationType
from scp_memory.models.memory import Memory
from scp_memory.models.provenance import Provenance
from scp_memory.services import audit_service, importance_service, relation_service
from scp_memory.services.errors import ServiceError

logger = logging.getLogger("scp_memory.consolidation")

_MAX_SUMMARY_CHARS = 2000


def _load_sources(db: Session, namespace: str, source_ids: list[str]) -> list[Memory]:
    unique_ids = list(dict.fromkeys(source_ids))  # dedupe, preserve order
    if len(unique_ids) < 2:
        raise ServiceError("consolidation requires at least two distinct source memories")

    rows = list(db.scalars(select(Memory).where(Memory.id.in_(unique_ids))))
    found = {m.id: m for m in rows}
    for mid in unique_ids:
        memory = found.get(mid)
        if (
            memory is None
            or memory.namespace != namespace
            or memory.state != MemoryState.active.value
        ):
            raise ServiceError(f"source memory '{mid}' is not an active memory in this namespace")
    return [found[mid] for mid in unique_ids]


def _naive_summary(sources: list[Memory]) -> str:
    joined = " | ".join(m.content for m in sources)
    text = f"Consolidated summary of {len(sources)} memories: {joined}"
    return text[:_MAX_SUMMARY_CHARS]


def consolidate(
    db: Session,
    *,
    namespace: str,
    source_ids: list[str],
    actor: str,
    summary: str | None = None,
) -> Memory:
    """Create a summary memory from sources; mark sources consolidated."""
    sources = _load_sources(db, namespace, source_ids)
    ids = [m.id for m in sources]

    memory = Memory(
        content=summary or _naive_summary(sources),
        type=MemoryType.summary.value,
        state=MemoryState.active.value,
        namespace=namespace,
        meta={"consolidated_from": ids},
    )
    memory.provenance = Provenance(
        source="consolidation",
        actor=actor,
        derivation={"kind": "consolidation", "sources": ids},
    )
    db.add(memory)
    db.flush()  # assign summary id + created_at
    importance_service.recompute(memory)

    audit_service.record(
        db,
        memory_id=memory.id,
        action=AuditAction.consolidate,
        actor=actor,
        diff={"summary_of": ids},
    )
    for source in sources:
        source.state = MemoryState.consolidated.value
        relation_service.add(
            db,
            src_id=memory.id,
            dst_id=source.id,
            relation=RelationType.derived_from,
        )
        audit_service.record(
            db,
            memory_id=source.id,
            action=AuditAction.consolidate,
            actor=actor,
            diff={
                "summary_id": memory.id,
                "state": {"before": "active", "after": "consolidated"},
            },
        )

    db.commit()
    db.refresh(memory)
    MEMORIES_CONSOLIDATED.inc()
    logger.info(
        "consolidation",
        extra={"namespace": namespace, "summary_id": memory.id, "sources": len(ids)},
    )
    return memory
