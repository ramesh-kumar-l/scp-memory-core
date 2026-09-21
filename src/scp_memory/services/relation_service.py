"""Relation service — writes edges into `memory_relations` (Phase 2).

The first write paths for the graph layer: consolidation records `derived_from`
edges, deduplication records `supersedes` edges. Mirrors the NetworkX graph that
arrives in a later phase. Callers own the transaction (no commit).
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from scp_memory.models.enums import RelationType
from scp_memory.models.relation import MemoryRelation


def add(db: Session, *, src_id: str, dst_id: str, relation: RelationType) -> MemoryRelation:
    """Append a directed edge src --relation--> dst."""
    edge = MemoryRelation(src_id=src_id, dst_id=dst_id, relation=relation.value)
    db.add(edge)
    return edge


def relations_from(db: Session, src_id: str) -> list[MemoryRelation]:
    """All outgoing edges from a memory (newest first)."""
    return list(
        db.scalars(
            select(MemoryRelation)
            .where(MemoryRelation.src_id == src_id)
            .order_by(MemoryRelation.created_at.desc())
        )
    )
