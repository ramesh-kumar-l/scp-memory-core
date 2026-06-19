"""Integration tests for the Phase 2 intelligence endpoints."""


def _create(client, content, ns="user:1", type_="fact"):
    return client.post(
        "/v1/memories",
        json={"content": content, "namespace": ns, "type": type_},
        headers={"X-Actor": "alice"},
    ).json()


def test_memory_read_exposes_importance(client):
    body = _create(client, "a durable fact")
    assert body["importance"] is not None
    assert 0.0 <= body["importance"] <= 1.0
    assert body["access_count"] == 0


def test_dedup_endpoint_merges_duplicates(client):
    _create(client, "user prefers dark mode please")
    _create(client, "user prefers dark mode please")

    resp = client.post("/v1/intelligence/dedup", json={"namespace": "user:1"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["merged_count"] == 1
    assert len(body["clusters"]) == 1

    # The default list now shows only the surviving canonical memory.
    listed = client.get("/v1/memories", params={"namespace": "user:1"}).json()
    assert listed["total"] == 1


def test_consolidate_endpoint_returns_summary(client):
    a = _create(client, "user upgraded plan")
    b = _create(client, "user added a teammate")

    resp = client.post(
        "/v1/intelligence/consolidate",
        json={"namespace": "user:1", "source_ids": [a["id"], b["id"]]},
        headers={"X-Actor": "alice"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["summary"]["type"] == "summary"
    assert body["source_ids"] == [a["id"], b["id"]]

    # Sources are now consolidated, not in the active list.
    listed = client.get("/v1/memories", params={"namespace": "user:1"}).json()
    ids = {m["id"] for m in listed["items"]}
    assert a["id"] not in ids and b["id"] not in ids
    assert body["summary"]["id"] in ids


def test_consolidate_validation_error_is_400(client):
    a = _create(client, "only one")
    resp = client.post(
        "/v1/intelligence/consolidate",
        json={"namespace": "user:1", "source_ids": [a["id"], "mem_missing"]},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "error"


def test_decay_endpoint_reports_scanned(client):
    _create(client, "recent fact")
    resp = client.post("/v1/intelligence/decay", json={"namespace": "user:1"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["scanned"] == 1
    assert body["decayed"] == []  # fresh memory survives
