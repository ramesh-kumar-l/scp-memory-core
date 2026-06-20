# 28 — Session Handoff

**Last updated:** 2026-06-20 · **Read this first, every session.**

## Last Session Summary

**Date:** 2026-06-20
**Goal:** Implement Phase 7 — Admin Console (Memory / Retrieval / Trust explorers +
Dashboard / Benchmarks / Settings); exit criteria = an **inspectable UI over all
signals**, on a production-stable footing.

### What was done
- **`console/` SPA (ADR-015):** Vite + React + TypeScript app reusing the official
  `@scp/memory-sdk` (Phase 5) as its only client. React Query for fetch/cache/state;
  React Router for the six screens. Design tokens (Inter, 8-pt grid, light+dark,
  semantic state/trust colors) in `src/theme/`.
- **Six screens:** Dashboard (health + counters + API SLOs from `/metrics`), Memory
  Explorer (+ MemoryDetail: fields, metadata, audit trail; create/delete; dedup/decay),
  Retrieval Inspector (per-signal score bars + weights + trust — explainability made
  visual), Trust Explorer (provenance/confidence/freshness bars + explanation),
  Benchmarks (live per-endpoint latency percentiles vs SLO targets), Settings
  (namespace / engine URL / actor / theme, persisted to localStorage).
- **Required states everywhere:** Empty / Loading (skeletons) / Error (friendly,
  actionable) + keyboard operability + WCAG-AA semantics.
- **Pure, tested core:** `src/api/metrics.ts` is a standalone Prometheus parser +
  histogram-quantile/error-ratio math (no DOM) — unit-tested.
- **Tests:** **8 console tests** (parser/quantile/error-ratio + UI primitives);
  `tsc` strict typecheck clean; production build green (~74 kB gzip).
- **Docs:** `docs/phase-7-admin-console.md`, `console/README.md`, ADR-015.

### Decisions / notes
- **Same-origin transport, no CORS.** The console calls relative paths; Vite proxies
  `/v1`, `/health`, `/metrics` to the engine in dev, and a reverse proxy forwards
  them in prod. **No engine code was changed** — the engine's no-CORS posture stands.
- **SDK is the single client** (DRY); ops-only endpoints (`/health/ready`,
  `/metrics`) use a thin fetch helper. In-console SLIs parse `/metrics` client-side
  (no Grafana dependency for the Dashboard/Benchmarks numbers).
- The console depends on the **built** SDK (`file:../sdks/typescript`) — run the SDK
  `npm run build` before the console `npm install` / `dev` / `build`.
- Console versioned independently (**0.6.0**). No engine/SDK version change.

### State
- Phase 7 **complete**, pending confirmation. **No commit made yet** — Phases 1–7
  are all uncommitted on `master`. (A live-contract check wrote a demo row to the
  dev `scp_memory.db`; harmless.)

## Where to Resume

**Next:** Phase 8 — Android Reference App (on-device semantic memory demo against
the engine). See [09-backlog](09-backlog.md).

> **Do not start Phase 8 without explicit approval** ([08-active-phase](08-active-phase.md)).

## First Actions Next Session
1. Read `07`, `08`, `28` (this file).
2. Confirm Phase 7 acceptance / get approval to begin Phase 8.
3. If approved, scope Phase 8 (on-device embedder story, engine connectivity, the
   minimum demo) before writing code.

## Resolved Decisions (2026-06-20)
- **SDK publishing → keep in-repo this cycle (ADR-013).** Publish at 1.0/API-freeze.
- **Production embedder → opt in at deployment (ADR-013).** Code default `hashing`.
- **Tracing → opt-in at deployment (ADR-014).** Default off; prod sets the flag + extra.
- **Console stack → Vite+React+TS, reuse SDK, same-origin/no-CORS (ADR-015).**

## Open Questions for User
- Approve Phase 7 and authorize Phase 8 (Android Reference App)?
- Commit the Phases 1–7 code now? (nothing has been committed yet)
- Console auth: add a login/session layer, or keep trusting the network boundary?
- Should trust adopt a real NLI model for corroboration/contradiction? (still deferred)

## Related

[07-current-state](07-current-state.md) · [08-active-phase](08-active-phase.md) · [09-backlog](09-backlog.md)
