"""Deploy assets are well-formed and define the Phase-6 SLOs (ADR-014)."""

import json
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_RULES = _ROOT / "deploy" / "observability" / "prometheus" / "rules" / "slo.rules.yml"
_DASHBOARD = _ROOT / "deploy" / "observability" / "grafana" / "dashboards" / "scp-overview.json"


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


def test_dashboard_is_valid_json_referencing_slis():
    text = _DASHBOARD.read_text(encoding="utf-8")
    dashboard = json.loads(text)  # raises on malformed JSON
    assert dashboard["uid"] == "scp-overview"
    # Panels must query the recording rules and the request histogram.
    assert "job:scp_api_errors:ratio_rate5m" in text
    assert "scp_api_request_duration_seconds_bucket" in text
