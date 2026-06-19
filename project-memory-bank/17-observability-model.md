# 17 — Observability Model

**Status:** Design intent · **Primary target:** Phase 6 (instrumentation added per feature throughout) · **Last updated:** 2026-06-20

Operability is a quality gate: metrics and logging are required for every feature,
not deferred wholesale to Phase 6. Phase 6 delivers the full stack and dashboards.

**Stack:** OpenTelemetry (instrumentation) → Prometheus (metrics) → Grafana
(dashboards). Decided in [ADR-009](25-adr-log.md).

## The Three Pillars

### Metrics (Prometheus)
- **API:** request rate, latency (p50/p95/p99), error rate per endpoint.
- **Memory:** memories created/updated/deleted, dedup merges, consolidations,
  decays.
- **Retrieval:** query latency, candidate counts, top-k size, mode mix
  (keyword/vector/hybrid).
- **Trust:** distribution of confidence/freshness on returned results.
- **Stores:** SQL query latency, Qdrant search latency.

### Logging (structured)
- JSON logs with correlation/trace IDs.
- Every mutation logs actor + action (mirrors audit, but operational).
- No memory *content* in logs by default (privacy) — IDs and metadata only.

### Tracing (OpenTelemetry)
- Spans across API → service → store(s) for each request.
- Retrieval traces show the keyword/vector/metadata/ranking stages — pairs with
  retrieval explainability.

## Principles

- **Every feature ships metrics + logs** (quality gate, [05](05-engineering-principles.md)).
- **Vendor-neutral:** OTel so backends are swappable.
- **Privacy-aware:** telemetry carries IDs/metadata, not memory content.

## Phase Notes

- Phases 1–5: each feature adds its metrics/logs/spans inline.
- Phase 6: consolidate into Prometheus + Grafana dashboards; SLOs defined.

## Related

[05-engineering-principles](05-engineering-principles.md) · [16-security-model](16-security-model.md) · [18-testing-strategy](18-testing-strategy.md)
