"""Unit tests for the DB-aware trust evaluation service (Phase 4)."""

from scp_memory.schemas.memory import MemoryCreate
from scp_memory.services import memory_service, trust_service


def _seed(db, content, *, ns="user:1", type_="fact", source="user"):
    return memory_service.create(
        db,
        MemoryCreate(content=content, namespace=ns, type=type_, source=source),
        actor="tester",
    )


def test_provenance_source_drives_quality(db):
    user_mem = _seed(db, "the user prefers dark mode", source="user")
    inferred_mem = _seed(db, "the user likely enjoys jazz music", source="inferred")

    user_trust = trust_service.evaluate(user_mem, neighbors=[])
    inferred_trust = trust_service.evaluate(inferred_mem, neighbors=[])

    assert user_trust.provenance_quality > inferred_trust.provenance_quality
    assert user_trust.explanation  # always explainable


def test_corroboration_raises_confidence(db):
    # Inferred provenance leaves headroom for corroboration to lift confidence
    # (user-stated memories already sit at the 1.0 ceiling).
    target = _seed(db, "the user prefers dark mode in the application", source="inferred")
    # A near-duplicate, same-type neighbour corroborates.
    supporter = _seed(db, "the user prefers dark mode across the application")
    unrelated = _seed(db, "favourite cuisine is italian pasta")

    with_support = trust_service.evaluate(target, neighbors=[supporter, unrelated])
    alone = trust_service.evaluate(target, neighbors=[unrelated])

    assert with_support.confidence > alone.confidence
    assert "corroborated by 1 memory" in with_support.explanation


def test_negation_divergence_is_treated_as_contradiction(db):
    target = _seed(db, "the user wants email notifications enabled for updates")
    contradictor = _seed(db, "the user does not want email notifications for updates")

    verdict = trust_service.evaluate(target, neighbors=[contradictor])
    assert "contradicted by 1 memory" in verdict.explanation


def test_evaluate_all_is_aligned_with_input(db):
    a = _seed(db, "alpha memory about scheduling")
    b = _seed(db, "beta memory about billing")

    results = trust_service.evaluate_all([a, b])
    assert len(results) == 2
    assert all(0.0 <= r.score <= 1.0 for r in results)


def test_evaluate_memory_respects_namespace(db):
    mem = _seed(db, "scoped memory", ns="tenant:a")
    assert trust_service.evaluate_memory(db, memory_id=mem.id, namespace="tenant:b") is None
    verdict = trust_service.evaluate_memory(db, memory_id=mem.id, namespace="tenant:a")
    assert verdict is not None
    assert verdict.score > 0.0
