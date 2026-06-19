"""Integration tests: API <-> service <-> SQLite, end-to-end (18-testing-strategy)."""


def _create(client, content="prefers dark mode", ns="user:123", actor="alice"):
    return client.post(
        "/v1/memories",
        json={
            "content": content,
            "namespace": ns,
            "type": "preference",
            "metadata": {"source": "settings"},
        },
        headers={"X-Actor": actor},
    )


def test_create_returns_201_with_active_memory(client):
    resp = _create(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"].startswith("mem_")
    assert body["state"] == "active"
    assert body["namespace"] == "user:123"
    assert body["metadata"] == {"source": "settings"}


def test_create_validation_error_is_422(client):
    resp = client.post("/v1/memories", json={"content": "", "namespace": "user:1"})
    assert resp.status_code == 422


def test_get_missing_returns_problem_shape(client):
    resp = client.get("/v1/memories/mem_does_not_exist")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "not_found"


def test_crud_roundtrip_and_audit_trail(client):
    created = _create(client).json()
    mem_id = created["id"]

    got = client.get(f"/v1/memories/{mem_id}")
    assert got.status_code == 200
    assert got.json()["last_accessed_at"] is not None

    patched = client.patch(
        f"/v1/memories/{mem_id}",
        json={"content": "prefers light mode"},
        headers={"X-Actor": "bob"},
    )
    assert patched.status_code == 200
    assert patched.json()["content"] == "prefers light mode"

    deleted = client.delete(f"/v1/memories/{mem_id}")
    assert deleted.status_code == 204

    # Soft-deleted: hidden from GET, but audit trail remains.
    assert client.get(f"/v1/memories/{mem_id}").status_code == 404
    audit = client.get(f"/v1/memories/{mem_id}/audit").json()
    actions = [e["action"] for e in audit["items"]]
    assert actions == ["delete", "update", "create"]
    assert audit["items"][1]["actor"] == "bob"


def test_list_filters_by_namespace(client):
    _create(client, content="a", ns="user:1")
    _create(client, content="b", ns="user:2")
    resp = client.get("/v1/memories", params={"namespace": "user:1"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["namespace"] == "user:1"


def test_namespace_scoped_get_blocks_other_tenant(client):
    mem_id = _create(client, ns="user:1").json()["id"]
    resp = client.get(f"/v1/memories/{mem_id}", params={"namespace": "user:2"})
    assert resp.status_code == 404


def test_health_and_metrics_endpoints(client):
    assert client.get("/health").json() == {"status": "ok"}
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "scp_memories_created_total" in metrics.text
