# Observability stack (Phase 6)

Runnable Prometheus + Grafana + Tempo + OpenTelemetry Collector pipeline for the
SCP Memory Engine. Implements the [observability model](../../project-memory-bank/17-observability-model.md)
and [ADR-009/014](../../project-memory-bank/25-adr-log.md).

```
app ──/metrics──▶ Prometheus ──┐
 │                              ├──▶ Grafana (dashboards + SLOs)
 └──OTLP──▶ otel-collector ──▶ Tempo ─┘ (traces, correlated with metrics)
```

## Run

From the repo root:

```bash
docker compose -f deploy/observability/docker-compose.yml up --build
```

| Service    | URL                     | Notes                                  |
|------------|-------------------------|----------------------------------------|
| Engine     | http://localhost:8000   | `/health`, `/health/ready`, `/metrics` |
| Prometheus | http://localhost:9090   | SLO recording + alert rules loaded     |
| Grafana    | http://localhost:3000   | admin / admin · "SCP Memory Engine" dir |

The app runs with `SCP_TRACING_ENABLED=true` and exports OTLP to the collector.

## SLOs

| SLO            | Target                          | Alert                         |
|----------------|---------------------------------|-------------------------------|
| Availability   | 99.9% non-5xx (0.1% budget)     | `ScpAvailabilityFastBurn`     |
| API latency    | p95 < 300ms, p99 < 1s           | `ScpApiLatency{P95,P99}High`  |
| Retrieval      | p95 `/v1/retrieval/search` <500ms | `ScpRetrievalLatencyP95High` |
| Liveness       | target scrapeable               | `ScpEngineDown`               |

Definitions and rationale: [`docs/phase-6-observability.md`](../../docs/phase-6-observability.md).

## Files

- `docker-compose.yml` — the full stack.
- `prometheus/prometheus.yml` — scrape config.
- `prometheus/rules/slo.rules.yml` — SLO recording + alerting rules.
- `otel-collector/config.yml` — OTLP → Tempo.
- `tempo/tempo.yml` — single-binary trace store (local; use object storage in prod).
- `grafana/provisioning/*` — datasources + dashboard providers.
- `grafana/dashboards/scp-overview.json` — overview + SLO dashboard.
