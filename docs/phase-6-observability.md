# Phase 6 — Observability

Consolidates the telemetry that earlier phases emitted inline into a runnable,
production-grade stack: **metrics + structured logs + distributed tracing +
defined SLOs**. Implements [17-observability-model](../project-memory-bank/17-observability-model.md)
and [ADR-009/014](../project-memory-bank/25-adr-log.md).

## What ships

| Pillar  | Mechanism                                                           |
|---------|---------------------------------------------------------------------|
| Metrics | Prometheus counters + the `scp_api_request_duration_seconds` histogram, scraped at `/metrics`. |
| Logs    | Structured JSON (`logging_config.py`); IDs/metadata only, never memory content; stamped with `trace_id`/`span_id` when tracing is active. |
| Traces  | OpenTelemetry, **opt-in** (`SCP_TRACING_ENABLED`); FastAPI + SQLAlchemy auto-instrumentation → OTLP → collector → Tempo. |
| Probes  | `/health` (liveness) and `/health/ready` (readiness — checks the DB). |
| SLOs    | Prometheus recording + alerting rules; Grafana SLO dashboard.       |

## Traced request path

When `SCP_TRACING_ENABLED=true` (needs the `[observability]` extra), each request
produces a span tree **API → service → store**: `FastAPIInstrumentor` opens the
server span and `SQLAlchemyInstrumentor` nests a span per DB statement. Spans
export over OTLP to the collector, which forwards to Tempo; Grafana correlates a
trace with the metrics around it, and logs carry the same `trace_id`.

Tracing is **off by default** so the test suite and offline dev path need no
OpenTelemetry install. Enabling it without the extra installed **fails loudly**
(same no-silent-degradation contract as the ADR-011 embedder).

## SLOs

| SLO            | SLI                                                   | Target                         | Alert                        |
|----------------|-------------------------------------------------------|--------------------------------|------------------------------|
| Availability   | non-5xx ÷ total requests                              | 99.9% (0.1% error budget)      | `ScpAvailabilityFastBurn`    |
| API latency    | `histogram_quantile` over the request histogram       | p95 < 300ms, p99 < 1s          | `ScpApiLatency{P95,P99}High` |
| Retrieval      | same, filtered to `/v1/retrieval/search`              | p95 < 500ms                    | `ScpRetrievalLatencyP95High` |
| Liveness       | `up{job="scp-memory-engine"}`                         | scrapeable                     | `ScpEngineDown`              |

Recording rules pre-compute the SLIs (`job:scp_api_errors:ratio_rate5m`,
`job:scp_api_latency:p95_5m`, …); the availability alert uses a multi-window
(5m ∧ 30m) burn condition to balance speed against noise. Rules live in
[`deploy/observability/prometheus/rules/slo.rules.yml`](../deploy/observability/prometheus/rules/slo.rules.yml).

## Run the stack

```bash
docker compose -f deploy/observability/docker-compose.yml up --build
```

Grafana → http://localhost:3000 (admin/admin), dashboard **SCP Memory Engine —
Overview & SLOs**. Prometheus → http://localhost:9090. See
[`deploy/observability/README.md`](../deploy/observability/README.md).

## Configuration

| Setting                 | Default | Purpose                                          |
|-------------------------|---------|--------------------------------------------------|
| `SCP_TRACING_ENABLED`   | `false` | Turn on OTLP tracing (needs `[observability]`).   |
| `SCP_OTLP_ENDPOINT`     | `""`    | OTLP traces endpoint; empty = OTel SDK defaults.  |

## Scope notes

- Metrics and logs require no extra install — only tracing is gated.
- The bundled Tempo uses local block storage (dev); back it with object storage
  (S3/GCS) in production.
- Manual per-stage retrieval spans (keyword/vector/ranking) remain a future
  refinement; auto-instrumentation already covers the full API→store path.
