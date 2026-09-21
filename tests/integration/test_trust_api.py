"""Integration tests for the Phase 4 trust layer (explain endpoint + retrieval)."""


def _create(client, content, ns="user:1", type_="fact", source=None):
    payload = {"content": content, "namespace": ns, "type": type_}
    if source:
        payload["source"] = source
    return client.post("/v1/memories", json=payload, headers={"X-Actor": "alice"}).json()


def test_trust_explain_endpoint_returns_breakdown(client):
    mem = _create(client, "the user prefers dark mode", source="user")

    resp = client.get(f"/v1/trust/{mem['id']}", params={"namespace": "user:1"})
    assert resp.status_code == 200
    body = resp.json()
    assert set(body) == {
        "provenance_quality",
        "confidence",
        "freshness",
        "score",
        "explanation",
    }
    assert body["provenance_quality"] == 1.0  # user-stated
    assert "high provenance" in body["explanation"]


def test_trust_explain_unknown_memory_is_404(client):
    resp = client.get("/v1/trust/does-not-exist", params={"namespace": "user:1"})
    assert resp.status_code == 404


def test_retrieval_results_carry_trust(client):
    _create(client, "the user prefers dark mode in the app", source="user")

    resp = client.post(
        "/v1/retrieval/search",
        json={"query": "dark mode", "namespace": "user:1"},
    )
    top = resp.json()["results"][0]
    assert top["trust"]["provenance_quality"] == 1.0
    assert top["signals"]["trust"] >= 0.0
    assert top["weights"]["trust"] > 0.0


def test_min_confidence_filter_excludes_low_trust(client):
    _create(client, "an inferred guess about the user", source="inferred")

    # Inferred, uncorroborated → confidence ~0.5; a 0.95 floor should exclude it.
    resp = client.post(
        "/v1/retrieval/search",
        json={"query": "inferred guess", "namespace": "user:1", "min_confidence": 0.95},
    )
    assert resp.status_code == 200
    assert resp.json()["results"] == []
