"""Unit tests for the hybrid retrieval orchestration."""

from scp_memory.schemas.memory import MemoryCreate
from scp_memory.schemas.retrieval import RetrieveRequest
from scp_memory.services import memory_service, retrieval_service


def _seed(db, content, ns="user:1", type_=None):
    payload = {"content": content, "namespace": ns}
    if type_:
        payload["type"] = type_
    return memory_service.create(db, MemoryCreate(**payload), actor="tester")


def test_hybrid_retrieval_ranks_relevant_first(db):
    _seed(db, "the user prefers dark mode in the application")
    _seed(db, "the user lives in the india standard timezone")
    _seed(db, "favourite food is pasta with tomato sauce")

    req = RetrieveRequest(query="dark mode preference", namespace="user:1", k=3)
    results = retrieval_service.search(db, req)

    assert results
    assert "dark mode" in results[0].memory.content
    # explainability contract: every signal is present (trust added in Phase 4).
    assert set(results[0].signals.keys()) == {
        "keyword",
        "vector",
        "metadata",
        "importance",
        "trust",
    }
    assert set(results[0].weights.keys()) == {"keyword", "vector", "importance", "trust"}


def test_namespace_isolation(db):
    _seed(db, "secret tenant a memory", ns="tenant:a")
    _seed(db, "secret tenant b memory", ns="tenant:b")

    results = retrieval_service.search(
        db, RetrieveRequest(query="secret memory", namespace="tenant:a")
    )
    assert all(r.memory.namespace == "tenant:a" for r in results)
    assert len(results) == 1


def test_keyword_mode_uses_only_lexical_signal(db):
    _seed(db, "qdrant vector search engine")
    results = retrieval_service.search(
        db, RetrieveRequest(query="qdrant", namespace="user:1", mode="keyword")
    )
    assert results
    assert results[0].signals["vector"] == 0.0


def test_retrieval_touches_returned_results(db):
    m = _seed(db, "a memory that will be retrieved and touched")
    assert m.access_count == 0

    retrieval_service.search(db, RetrieveRequest(query="memory retrieved", namespace="user:1"))
    db.refresh(m)
    assert m.access_count == 1
    assert m.last_accessed_at is not None


def test_empty_namespace_returns_no_results(db):
    results = retrieval_service.search(db, RetrieveRequest(query="anything", namespace="empty"))
    assert results == []


def test_type_filter_constrains_candidates(db):
    _seed(db, "user prefers concise answers", type_="preference")
    _seed(db, "user prefers concise answers", type_="fact")

    results = retrieval_service.search(
        db,
        RetrieveRequest(query="concise answers", namespace="user:1", type="preference"),
    )
    assert results
    assert all(r.memory.type == "preference" for r in results)
