"""Python SDK against the real app in-process (httpx ASGI transport, no network).

Exercises the full surface the SDK exposes: CRUD + audit, intelligence, hybrid
retrieval (with trust), and the trust explain endpoint — proving the published
client speaks the live API contract.
"""

import pytest
from fastapi.testclient import TestClient
from scp_memory_sdk import NotFoundError, SCPMemoryClient

from scp_memory.api.app import create_app
from scp_memory.api.deps import get_db


@pytest.fixture
def sdk(session_factory):
    app = create_app(init=False)

    def _override_get_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db
    # TestClient is a sync httpx.Client subclass that runs the ASGI app in-process.
    http = TestClient(app)
    client = SCPMemoryClient(http_client=http, actor="alice")
    try:
        yield client
    finally:
        http.close()


def test_health(sdk):
    assert sdk.health() == {"status": "ok"}


def test_crud_roundtrip_and_audit(sdk):
    mem = sdk.memories.create(
        content="the user prefers dark mode",
        namespace="user:1",
        type="preference",
        source="settings",
    )
    assert mem.id and mem.type == "preference"

    fetched = sdk.memories.get(mem.id, namespace="user:1")
    assert fetched.content == "the user prefers dark mode"

    updated = sdk.memories.update(mem.id, content="the user prefers light mode", namespace="user:1")
    assert updated.content == "the user prefers light mode"

    page = sdk.memories.list(namespace="user:1")
    assert page.total >= 1 and any(m.id == mem.id for m in page.items)

    audit = sdk.memories.audit(mem.id)
    actions = {e.action for e in audit.items}
    assert {"create", "update"} <= actions

    sdk.memories.delete(mem.id, namespace="user:1")
    with pytest.raises(NotFoundError):
        sdk.memories.get(mem.id, namespace="user:1")


def test_retrieval_carries_trust(sdk):
    sdk.memories.create(
        content="the user prefers dark mode in the app",
        namespace="user:1",
        type="preference",
        source="user",
    )
    resp = sdk.retrieval.search(query="dark mode", namespace="user:1")
    assert resp.count >= 1
    top = resp.results[0]
    assert top.trust.provenance_quality == 1.0  # user-stated
    assert top.weights["trust"] > 0.0
    assert top.signals.trust >= 0.0


def test_min_confidence_filter(sdk):
    sdk.memories.create(
        content="an inferred guess about the user",
        namespace="user:1",
        type="fact",
        source="inferred",
    )
    resp = sdk.retrieval.search(query="inferred guess", namespace="user:1", min_confidence=0.95)
    assert resp.results == []


def test_trust_explain(sdk):
    mem = sdk.memories.create(content="the user lives in Berlin", namespace="user:1", source="user")
    verdict = sdk.trust.explain(mem.id, namespace="user:1")
    assert verdict.provenance_quality == 1.0
    assert "high provenance" in verdict.explanation
    with pytest.raises(NotFoundError):
        sdk.trust.explain("missing", namespace="user:1")


def test_intelligence_consolidate(sdk):
    a = sdk.memories.create(content="user likes tea", namespace="user:2")
    b = sdk.memories.create(content="user likes green tea", namespace="user:2")
    result = sdk.intelligence.consolidate(namespace="user:2", source_ids=[a.id, b.id])
    assert result.summary.id
    assert set(result.source_ids) == {a.id, b.id}
