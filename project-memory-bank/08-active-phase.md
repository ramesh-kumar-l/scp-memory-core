# 08 — Active Phase

**Last updated:** 2026-06-20 · **Read this first, every session.**

> Doubles as the project's **active-context** save state (05 working agreement).

## Active Phase: 6 — Observability ✅ complete (awaiting approval for Phase 7)

### Goal
Make the engine **operable and production-stable**: consolidate per-feature
telemetry into a runnable stack with **dashboards, a traced request path, and
defined SLOs** (the Phase-6 exit criteria), without burdening the hermetic/offline
test path.

### Deliverables
- [x] **OTel distributed tracing** (ADR-014): `observability/tracing.py`,
  opt-in via `SCP_TRACING_ENABLED` + `[observability]` extra; FastAPI + SQLAlchemy
  auto-instrumentation → OTLP → collector → Tempo; fail-loud if the extra is absent
- [x] **Trace↔log correlation**: `trace_id`/`span_id` stamped into JSON logs
  (guarded import — logging unchanged without the extra)
- [x] **Liveness + readiness probes**: `/health` (process) + `/health/ready` (DB check, 503 when down)
- [x] **SLOs codified**: Prometheus recording + multi-window-burn alert rules
- [x] **Runnable stack**: `deploy/observability/` docker-compose (app + collector +
  Tempo + Prometheus + Grafana) + provisioned dashboard + root `Dockerfile`
- [x] Tests (tracing/logging/ops-API/deploy-assets), `docs/phase-6-observability.md`

### Exit Criteria (all met)
- **Dashboards** — provisioned Grafana "Overview & SLOs" dashboard over Prometheus + Tempo.
- **Traced request path** — opt-in OTel spans cover API→service→store; logs carry the `trace_id`.
- **Defined SLOs** — availability 99.9%; API p95<300ms / p99<1s; retrieval p95<500ms;
  liveness — as Prometheus recording + alert rules.
- Python: **105 tests** passing (+ benchmark); ruff + black clean.
- Strict modularity: longest new source file `tracing.py` 75 lines (none > 300).
- Quality gates satisfied ([05-engineering-principles](05-engineering-principles.md)).

### Status
**Complete** (pending user confirmation). Awaiting approval to start Phase 7.

### Key decisions
- **Tracing is opt-in, off by default.** Metrics + logs stay always-on; only
  tracing is gated behind `[observability]`, so CI/offline dev need no
  OpenTelemetry. Explicit enable without the extra **fails loudly** (mirrors the
  ADR-011 embedder contract).
- **SLOs live as code** (Prometheus rules) and are visualised in a provisioned
  dashboard; availability uses a multi-window (5m∧30m) burn alert.
- **Vendor-neutral** (OTLP) so the trace backend is swappable; bundled Tempo uses
  local storage (use object storage in prod). Engine bumped to **0.5.0**; no DB migrations.

---

## ⛔ Stop Rule (operating model)

> One phase is active at a time. **Do NOT begin Phase 7 (Admin Console) without
> explicit user approval.** Never work ahead or skip phases.

At the end of any phase: update `07`, `08`, `28`, then **stop** and wait for
explicit instruction.

## Next Phase (do not start yet)

**Phase 7 — Admin Console:** Dashboard, Memory Explorer, Retrieval Inspector,
Trust Explorer, Benchmarks, Settings (design system in
[19-ui-design-system](19-ui-design-system.md)). Scoped in [09-backlog](09-backlog.md).

## Related

[07-current-state](07-current-state.md) · [28-session-handoff](28-session-handoff.md) · [23-roadmap](23-roadmap.md)
