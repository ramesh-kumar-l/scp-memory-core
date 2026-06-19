"""Deduplication merges near-duplicates, keeping a canonical memory."""

from scp_memory.models.enums import MemoryState, RelationType
from scp_memory.schemas.memory import MemoryCreate
from scp_memory.services import dedup_service, memory_service, relation_service


def _create(db, content, ns="user:1"):
    return memory_service.create(db, MemoryCreate(content=content, namespace=ns), actor="t")


def test_near_duplicates_are_merged_with_supersedes_edge(db):
    a = _create(db, "user prefers dark mode please")
    b = _create(db, "user prefers dark mode please")

    clusters = dedup_service.run(db, namespace="user:1")
    assert len(clusters) == 1
    canonical_id = clusters[0].canonical_id
    merged_ids = clusters[0].merged_ids
    assert len(merged_ids) == 1
    assert {canonical_id, *merged_ids} == {a.id, b.id}

    # The merged memory is archived; the canonical stays active.
    db.refresh(a)
    db.refresh(b)
    archived = a if a.id in merged_ids else b
    assert archived.state == MemoryState.archived.value

    edges = relation_service.relations_from(db, canonical_id)
    assert any(
        e.dst_id in merged_ids and e.relation == RelationType.supersedes.value for e in edges
    )


def test_distinct_memories_are_not_merged(db):
    _create(db, "the sky is blue today")
    _create(db, "quarterly revenue rose twelve percent")
    clusters = dedup_service.run(db, namespace="user:1")
    assert clusters == []


def test_different_types_are_not_merged(db):
    from scp_memory.models.enums import MemoryType

    memory_service.create(
        db,
        MemoryCreate(content="same words here", namespace="user:1", type=MemoryType.fact),
        actor="t",
    )
    memory_service.create(
        db,
        MemoryCreate(content="same words here", namespace="user:1", type=MemoryType.preference),
        actor="t",
    )
    assert dedup_service.run(db, namespace="user:1") == []
