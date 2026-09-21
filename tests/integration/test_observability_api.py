"""Ops endpoints: liveness, readiness, and the Prometheus scrape (Phase 6)."""


def test_liveness_probe(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_readiness_probe_reports_db_ok(client):
    resp = client.get("/health/ready")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ready", "database": "ok"}


def test_metrics_endpoint_exposes_prometheus_text(client):
    # Generate some activity so counters/histograms have samples.
    client.post(
        "/v1/memories",
        json={"content": "the user prefers dark mode", "namespace": "user:1", "type": "fact"},
        headers={"X-Actor": "alice"},
    )

    resp = client.get("/metrics")
    assert resp.status_code == 200
    body = resp.text
    assert "scp_memories_created_total" in body
    assert "scp_api_request_duration_seconds" in body
