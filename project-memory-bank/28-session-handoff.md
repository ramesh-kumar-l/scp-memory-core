# 28 — Session Handoff

**Last updated:** 2026-06-20 · **Read this first, every session.**

## Last Session Summary

**Date:** 2026-06-20
**Goal:** Implement Phase 6 — Observability (Prometheus + Grafana + OTel tracing +
SLOs); exit criteria = dashboards + traced request path + defined SLOs, on a
production-stable footing.

### What was done
- **OTel distributed tracing (ADR-014):** `observability/tracing.py`
  (`configure_tracing`) — **opt-in** via `SCP_TRACING_ENABLED` + the new
  `[observability]` extra; FastAPI + SQLAlchemy auto-instrumentation gives the
  API→service→store span tree, exported over OTLP. Wired into `create_app`. Enabling
  without the extra **fails loudly**. `config.Settings` gained `tracing_enabled` /
  `otlp_endpoint`.
- **Trace↔log correlation:** `logging_config.py` stamps `trace_id`/`span_id` into
  JSON logs via a guarded OTel import (logging unchanged when the extra is absent).
- **Probes:** added `/health/ready` (DB check, 503 when down) beside liveness
  `/health`; `/metrics` retained. (`api/routes/health.py`.)
- **SLOs as code + runnable stack:** `deploy/observability/` — docker-compose
  (app + OTel collector + Tempo + Prometheus + Grafana), Prometheus scrape +
  `slo.rules.yml` (recording + multi-window-burn alerts), Grafana datasource +
  dashboard provisioning (`scp-overview.json`). Root `Dockerfile` (non-root).
- **Tests:** Python **105 passing** (+2 tracing, +2 logging, +3 ops-API, +2
  deploy-asset). ruff + black clean.
- **Docs:** `docs/phase-6-observability.md` (incl. SLO definitions), ADR-014 in
  `25-adr-log.md`, `deploy/observability/README.md`.

### Decisions / notes
- **Tracing is opt-in; metrics + logs stay always-on.** Only tracing is gated, so
  CI/offline dev need no OpenTelemetry. Vendor-neutral (OTLP) — backend swappable.
- **SLOs:** availability 99.9% (0.1% budget); API p95<300ms / p99<1s; retrieval
  p95<500ms; liveness. Codified as Prometheus rules + a Grafana dashboard.
- Engine bumped **0.4.0 → 0.5.0**; SDKs unchanged (0.5.0). No DB migrations.

### State
- Phase 6 **complete**, pending confirmation. **No commit made yet** — Phases 1–6
  are all uncommitted on `master`.

## Where to Resume

**Next:** Phase 7 — Admin Console (Dashboard, Memory Explorer, Retrieval Inspector,
Trust Explorer, Benchmarks, Settings; design system in
[19-ui-design-system](19-ui-design-system.md)). See [09-backlog](09-backlog.md).

> **Do not start Phase 7 without explicit approval** ([08-active-phase](08-active-phase.md)).

## First Actions Next Session
1. Read `07`, `08`, `28` (this file).
2. Confirm Phase 6 acceptance / get approval to begin Phase 7.
3. If approved, follow the Phase 7 backlog with all quality gates.

## Resolved Decisions (2026-06-20)
- **SDK publishing → keep in-repo this cycle (ADR-013).** Full publish deferred to
  the 1.0 / API-freeze milestone.
- **Production embedder → opt in at deployment, not in code (ADR-013).** Code
  default stays `hashing`; prod sets `SCP_EMBEDDER=sentence-transformers`.
- **Tracing → opt-in at deployment (ADR-014).** Default off; prod sets
  `SCP_TRACING_ENABLED=true` with the `[observability]` extra + an OTLP endpoint.

## Open Questions for User
- Approve Phase 6 and authorize Phase 7 (Admin Console)?
- Commit the Phases 1–6 code now? (nothing has been committed yet)
- Should trust adopt a real NLI model for corroboration/contradiction? (still deferred)

## Related

[07-current-state](07-current-state.md) · [08-active-phase](08-active-phase.md) · [09-backlog](09-backlog.md)
