# Phase 7 — Admin Console

An inspectable web UI over every signal the engine exposes. The console is a
**Vite + React + TypeScript** SPA in [`console/`](../console/README.md) that talks
to the engine through the official `@scp/memory-sdk` (Phase 5), so it exercises the
same contract as any other client. Decision recorded in
[ADR-015](../project-memory-bank/25-adr-log.md).

## Screens

| Screen | Signals made visible |
| --- | --- |
| **Dashboard** | Liveness (`/health` reachability) + readiness (`/health/ready`); memory/intelligence/retrieval/trust counters and API SLOs (error rate, p50/p95/p99) parsed from `/metrics`. |
| **Memory Explorer** | Filterable, paged list per namespace; create/delete; per-memory fields, metadata, and the append-only **audit trail**. Dedup/decay passes. |
| **Retrieval Inspector** | Runs hybrid retrieval; renders each candidate's fused score split into **per-signal bars** (keyword/vector/metadata/importance/trust) with the applied weights, plus the trust breakdown and explanation. |
| **Trust Explorer** | Provenance / confidence / freshness bars + the engine's explanation for a chosen memory. |
| **Benchmarks** | Per-endpoint latency percentiles derived live from the request histogram, checked against the Phase-6 SLO targets (300 ms API, 500 ms retrieval). |
| **Settings** | Active namespace, engine base URL, audit actor, light/dark theme — persisted to `localStorage`. |

Every screen implements the required **Empty / Loading / Error** states plus
keyboard operability and WCAG-AA semantics (`role`/`aria`, focus rings,
reduced-motion) from [19-ui-design-system](../project-memory-bank/19-ui-design-system.md).

## Architecture

- **React Query** owns fetch/cache and the loading/error state machine; **React
  Router** maps the six screens. Design tokens (Inter, 8-pt grid, light+dark,
  semantic state/trust colors) live in `src/theme/`.
- **Same-origin transport, no CORS.** The console calls relative paths. In dev the
  Vite server proxies `/v1`, `/health`, `/metrics` to the engine
  (`VITE_ENGINE_URL`, default `http://localhost:8000`); in production the static
  bundle is served behind a reverse proxy that forwards those paths. The engine is
  **not modified** ([16-security-model](../project-memory-bank/16-security-model.md)).
- **Explainability is the product.** The score bar is the core primitive: retrieval
  and trust both decompose a number into the parts that produced it.
- **Strict modularity:** every file is under 300 lines (largest 233).

## Verification

- `npm run typecheck` — clean (strict TS).
- `npm run test` — 8 tests: the Prometheus parser + quantile/error-ratio math, and
  UI-primitive rendering (states, badges, score meter).
- `npm run build` — production bundle (~74 kB gzip).
- Data contracts confirmed against a live engine: `/health/ready`, memory
  CRUD/list, retrieval, `/v1/trust/{id}`, and `/metrics` shapes.

## Run

```bash
cd sdks/typescript && npm install && npm run build   # build the SDK dependency
cd ../../console && npm install && npm run dev        # http://localhost:5173
```

## Deferred to production hardening

- Multi-origin / hosted console (would add the opt-in CORS allowlist to the engine).
- Auth/session in front of the console (today it trusts the network boundary).
- Trend charts over time (Benchmarks shows current percentiles; historical series
  belong in Grafana/Tempo from Phase 6).
