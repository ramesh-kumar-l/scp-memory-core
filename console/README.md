# SCP Memory — Admin Console (Phase 7)

An inspectable UI over every signal the engine exposes: memory CRUD + audit,
explainable hybrid retrieval, the trust layer, and live SLO metrics. Built on the
official `@scp/memory-sdk` so the console exercises the same contract as any client.

## Screens

| Screen | What it shows |
| --- | --- |
| **Dashboard** | Liveness/readiness + memory/retrieval/trust counters and API SLOs from `/metrics`. |
| **Memory Explorer** | Browse/filter/create/delete memories; per-memory fields + audit trail. |
| **Retrieval Inspector** | Run a query; see each candidate's per-signal scores, weights, and trust. |
| **Trust Explorer** | Provenance / confidence / freshness breakdown + explanation for a memory. |
| **Benchmarks** | Live per-endpoint latency percentiles vs the Phase-6 SLO targets. |
| **Settings** | Active namespace, engine base URL, audit actor, light/dark theme. |

Every screen implements the required Empty / Loading / Error / keyboard / a11y
states (`19-ui-design-system`).

## Architecture

- **Vite + React + TypeScript** SPA; **React Query** for fetch/cache/state;
  **React Router** for the six screens.
- Talks to the engine on the **same origin** (relative paths). In dev, Vite
  proxies `/v1`, `/health`, `/metrics` to the engine — so the engine needs **no
  CORS change** (`16-security-model`). In production, serve the static bundle
  behind a reverse proxy that forwards those paths to the engine.
- Strict modularity: every file is under 300 lines.

## Develop

```bash
# 1. Build the SDK the console depends on (once / on SDK change)
cd ../sdks/typescript && npm install && npm run build

# 2. Run the console against a local engine (default http://localhost:8000)
cd ../../console && npm install
VITE_ENGINE_URL=http://localhost:8000 npm run dev   # http://localhost:5173
```

`npm run typecheck` · `npm run test` · `npm run build`.
