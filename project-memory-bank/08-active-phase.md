# 08 — Active Phase

**Last updated:** 2026-06-20 · **Read this first, every session.**

> Doubles as the project's **active-context** save state (05 working agreement).

## Active Phase: 7 — Admin Console ✅ complete (awaiting approval for Phase 8)

### Goal
Deliver an **inspectable UI over all signals** — memory, retrieval explainability,
trust, and live SLOs — as a production-stable web console, reusing the official SDK
and the design system, without touching engine code.

### Deliverables
- [x] **`console/` SPA** (Vite + React + TS, ADR-015) reusing `@scp/memory-sdk`;
  React Query (fetch/cache/state) + React Router (six screens); design tokens
  (Inter, 8-pt grid, light+dark, semantic state/trust colors) in `src/theme/`
- [x] **Dashboard** — liveness + readiness + memory/intelligence/retrieval/trust
  counters and API SLOs (error rate, p50/p95/p99) parsed from `/metrics`
- [x] **Memory Explorer** — filter/page/create/delete + per-memory fields, metadata,
  and the append-only audit trail; dedup/decay passes
- [x] **Retrieval Inspector** — per-signal score bars + weights + trust (explainability)
- [x] **Trust Explorer** — provenance/confidence/freshness bars + explanation
- [x] **Benchmarks** — live per-endpoint latency percentiles vs SLO targets
- [x] **Settings** — namespace / engine URL / actor / theme (persisted)
- [x] Required Empty/Loading/Error/keyboard/a11y states on every screen;
  `docs/phase-7-admin-console.md`

### Exit Criteria (all met)
- **Inspectable UI over all signals** — six screens cover CRUD+audit, retrieval
  explainability, trust, and SLOs; explainability is visual via the score-bar primitive.
- TypeScript: `tsc` strict typecheck clean; **8 console tests** (Prometheus parser +
  quantile/error-ratio math; UI-primitive rendering); production build green (~74 kB gz).
- Data contracts verified against a live engine (`/health/ready`, CRUD/list,
  retrieval, `/v1/trust/{id}`, `/metrics`).
- Strict modularity: largest console file 233 lines (none > 300).
- **Zero engine changes** — same-origin transport (Vite proxy / reverse proxy).

### Status
**Complete** (pending user confirmation). Awaiting approval to start Phase 8.

### Key decisions
- **Reuse the SDK as the only client** (DRY) — the console exercises the same
  contract as any consumer; ops-only endpoints use a thin fetch helper.
- **Same-origin, no CORS** — relative paths proxied in dev, reverse-proxied in prod;
  the engine's security posture is untouched ([16-security-model](16-security-model.md)).
- **In-console SLIs parse `/metrics` client-side** (no Grafana dependency for the
  Dashboard/Benchmarks numbers). Console versioned independently (**0.6.0**).

---

## ⛔ Stop Rule (operating model)

> One phase is active at a time. **Do NOT begin Phase 8 (Android Reference App)
> without explicit user approval.** Never work ahead or skip phases.

At the end of any phase: update `07`, `08`, `28`, then **stop** and wait for
explicit instruction.

## Next Phase (do not start yet)

**Phase 8 — Android Reference App:** on-device semantic memory demo against the
engine. Scoped in [09-backlog](09-backlog.md).

> **Prep done (2026-06-20):** a self-contained build spec
> (`android-app-system-prompt.md`) and a consolidated API-contract reference
> (`29-api-contracts.md`) now exist, designed to be handed to a separate **Claude
> Design** session. Writing the spec is **not** starting Phase 8 — no app code has
> been written. The stop rule above still applies: do not implement Phase 8 here
> without explicit approval.

## Related

[07-current-state](07-current-state.md) · [28-session-handoff](28-session-handoff.md) · [23-roadmap](23-roadmap.md) · [../docs/phase-7-admin-console.md](../docs/phase-7-admin-console.md)
