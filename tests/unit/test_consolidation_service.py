"""Consolidation merges sources into a summary with provenance + edges."""

import pytest

from scp_memory.models.enums import MemoryState, MemoryType, RelationType
from scp_memory.schemas.memory import MemoryCreate
from scp_memory.services import consolidation_service, memory_service, relation_service
from scp_memory.services.errors import ServiceError


def _create(db, content, ns="user:1"):
    return memory_service.create(db, MemoryCreate(content=content, namespace=ns), actor="t")


def test_consolidate_creates_summary_and_marks_sources(db):
    a = _create(db, "user upgraded to pro plan")
    b = _create(db, "user enabled two-factor auth")

    summary = consolidation_service.consolidate(
        db, namespace="user:1", source_ids=[a.id, b.id], actor="t"
    )

    assert summary.type == MemoryType.summary.value
    assert summary.state == MemoryState.active.value
    assert summary.provenance.derivation["sources"] == [a.id, b.id]

    db.refresh(a)
    db.refresh(b)
    assert a.state == MemoryState.consolidated.value
    assert b.state == MemoryState.consolidated.value

    edges = relation_service.relations_from(db, summary.id)
    dst = {e.dst_id for e in edges if e.relation == RelationType.derived_from.value}
    assert dst == {a.id, b.id}


def test_consolidate_uses_provided_summary_text(db):
    a = _create(db, "alpha")
    b = _create(db, "beta")
    summary = consolidation_service.consolidate(
        db, namespace="user:1", source_ids=[a.id, b.id], actor="t", summary="A and B happened"
    )
    assert summary.content == "A and B happened"


def test_consolidate_requires_two_distinct_active_sources(db):
    a = _create(db, "lonely")
    with pytest.raises(ServiceError):
        consolidation_service.consolidate(
            db, namespace="user:1", source_ids=[a.id, a.id], actor="t"
        )


def test_consolidate_rejects_cross_namespace_source(db):
    a = _create(db, "x", ns="user:1")
    b = _create(db, "y", ns="user:2")
    with pytest.raises(ServiceError):
        consolidation_service.consolidate(
            db, namespace="user:1", source_ids=[a.id, b.id], actor="t"
        )
