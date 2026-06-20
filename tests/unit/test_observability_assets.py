"""Deploy assets are well-formed and define the Phase-6 SLOs (ADR-014)."""

import json
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_OBS = _ROOT / "deploy" / "observability"
_RULES = _OBS / "prometheus" / "rules" / "slo.rules.yml"
_DASHBOARD = _OBS / "grafana" / "dashboards" / "scp-overview.json"
_PROMETHEUS = _OBS / "prometheus" / "prometheus.yml"
_ALERTMANAGER = _OBS / "alertmanager" / "alertmanager.yml"


def test_slo_rules_parse_and_declare_the_slos():
    yaml = pytest.importorskip("yaml")
    data = yaml.safe_load(_RULES.read_text(encoding="utf-8"))

    group_names = {g["name"] for g in data["groups"]}
    assert {"scp-slo-recording", "scp-slo-alerts"} <= group_names

    alerts = {r["alert"] for g in data["groups"] for r in g["rules"] if "alert" in r}
    assert {
        "ScpAvailabilityFastBurn",
        "ScpApiLatencyP95High",
        "ScpApiLatencyP99High",
        "ScpRetrievalLatencyP95High",
        "ScpEngineDown",
    } <= alerts


def test_prometheus_wires_alertmanager():
    yaml = pytest.importorskip("yaml")
    data = yaml.safe_load(_PROMETHEUS.read_text(encoding="utf-8"))
    targets = [
        t
        for am in data["alerting"]["alertmanagers"]
        for sc in am["static_configs"]
        for t in sc["targets"]
    ]
    assert any("alertmanager" in t for t in targets)


def test_alertmanager_routes_every_alert_severity():
    yaml = pytest.importorskip("yaml")
    am = yaml.safe_load(_ALERTMANAGER.read_text(encoding="utf-8"))
    rules = yaml.safe_load(_RULES.read_text(encoding="utf-8"))

    # Every severity the SLO rules emit must have a matching child route.
    emitted = {
        r["labels"]["severity"]
        for g in rules["groups"]
        for r in g["rules"]
        if "alert" in r and "severity" in r.get("labels", {})
    }
    routed = " ".join(str(child.get("matchers", "")) for child in am["route"]["routes"])
    for severity in emitted:
        assert severity in routed, f"severity '{severity}' is not routed"

    receivers = {r["name"] for r in am["receivers"]}
    assert {"pager", "tickets", "default"} <= receivers
    assert am["inhibit_rules"]  # engine-down inhibition present


def test_dashboard_is_valid_json_referencing_slis():
    text = _DASHBOARD.read_text(encoding="utf-8")
    dashboard = json.loads(text)  # raises on malformed JSON
    assert dashboard["uid"] == "scp-overview"
    # Panels must query the recording rules and the request histogram.
    assert "job:scp_api_errors:ratio_rate5m" in text
    assert "scp_api_request_duration_seconds_bucket" in text
