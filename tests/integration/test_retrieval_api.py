"""Integration tests for the Phase 3 hybrid retrieval endpoint."""


def _create(client, content, ns="user:1", type_="fact"):
    return client.post(
        "/v1/memories",
        json={"content": content, "namespace": ns, "type": type_},
        headers={"X-Actor": "alice"},
    ).json()


def test_search_returns_explainable_ranked_results(client):
    _create(client, "the user prefers dark mode in the app")
    _create(client, "the user timezone is india standard time")

    resp = client.post(
        "/v1/retrieval/search",
        json={"query": "dark mode", "namespace": "user:1", "k": 5},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["mode"] == "hybrid"
    assert body["count"] >= 1
    top = body["results"][0]
    assert "dark mode" in top["memory"]["content"]
    assert set(top["signals"]) == {"keyword", "vector", "metadata", "importance", "trust"}
    assert 0.0 <= top["score"] <= 1.0
    # Phase 4: every result carries an explainable trust verdict.
    assert set(top["trust"]) == {
        "provenance_quality",
        "confidence",
        "freshness",
        "score",
        "explanation",
    }
    assert top["trust"]["explanation"]


def test_search_respects_namespace(client):
    _create(client, "alpha tenant fact", ns="tenant:a")
    _create(client, "beta tenant fact", ns="tenant:b")

    resp = client.post(
        "/v1/retrieval/search",
        json={"query": "tenant fact", "namespace": "tenant:a"},
    )
    body = resp.json()
    assert body["count"] == 1
    assert body["results"][0]["memory"]["namespace"] == "tenant:a"


def test_empty_namespace_returns_empty(client):
    resp = client.post(
        "/v1/retrieval/search",
        json={"query": "nothing here", "namespace": "ghost"},
    )
    assert resp.status_code == 200
    assert resp.json()["results"] == []


def test_validation_rejects_blank_query(client):
    resp = client.post(
        "/v1/retrieval/search",
        json={"query": "", "namespace": "user:1"},
    )
    assert resp.status_code == 422
