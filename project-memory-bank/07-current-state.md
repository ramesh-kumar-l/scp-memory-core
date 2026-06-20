# 07 — Current State

**Last updated:** 2026-06-20 · **Read this first, every session.**

> Doubles as the project's **implementation-status** save state (05 working
> agreement): update on every major feature / phase boundary.

## Snapshot

- **Phase:** 7 — Admin Console **complete** (pending approval to start Phase 8).
- **Repository:** `scp-memory-core`, branch `master`. Python package, two client
  SDKs, an observability deploy stack, an **admin console SPA**, tests, CI, docs,
  examples, and the memory bank.
- **Application code:** Memory Core (Phase 1) + Intelligence (Phase 2) + Hybrid
  Retrieval (Phase 3) + Trust Layer (Phase 4) + SDKs (Phase 5) + Observability
  (Phase 6). Phase 7 adds the **Admin Console** (`console/`): a Vite + React + TS
  SPA over the full signal surface — Dashboard, Memory Explorer, Retrieval
  Inspector, Trust Explorer, Benchmarks, Settings — reusing `@scp/memory-sdk` and
  talking to the engine same-origin (no CORS / no engine change).
- **Memory bank:** all 29 files (`00`–`28`) current.
- **Version:** engine 0.5.0; SDKs 0.5.0; console 0.6.0.

## What Exists (code)

- **Package** `src/scp_memory/` (src layout, strict modularity — all files < 300
  lines; longest 192):
  - `models/` — `Memory` (with `importance` + `access_count`), `Provenance`,
    `AuditEvent`, `MemoryRelation`, enums, id helpers.
  - `intelligence/` — `scoring.py` (importance), `similarity.py` (lexical Jaccard).
  - `retrieval/` — `embedding.py` (`HashingEmbedder` + cosine, pure), `keyword.py`
    (BM25, pure), `fusion.py` (weighted + RRF, pure; trust dimension), `config.py`,
    `local_embedder.py` (offline sentence-transformers, opt-in), `embedder_factory.py`
    (selects embedder via `SCP_EMBEDDER`).
  - `trust/` — `provenance.py`, `freshness.py`, `confidence.py`, `score.py`,
    `explain.py`, `config.py` (all pure, I/O-free).
  - `services/` — `memory_service`, `audit_service`, `importance_service`,
    `dedup_service`, `consolidation_service`, `decay_service`, `relation_service`,
    `retrieval_service`, `vector_backend` (brute-force default), `qdrant_backend`
    (optional, integration-only), `trust_service` (DB-aware, no writes).
  - `api/` — FastAPI factory, routes (`/v1/memories` CRUD + `/audit`,
    `/v1/intelligence/{decay,dedup,consolidate}`, `/v1/retrieval/search`,
    `/v1/trust/{memory_id}`, `/health`, `/health/ready`, `/metrics`);
    `middleware.py` (request-id + latency histogram).
  - `observability/` — `tracing.py` (`configure_tracing`: opt-in OTel, FastAPI +
    SQLAlchemy auto-instrumentation, fail-loud if the extra is absent).
  - `db/`, `config.py` (+ vector-backend/Qdrant + tracing settings),
    `logging_config.py` (JSON + trace correlation), `metrics.py` (+ retrieval &
    trust counters).
- **SDKs** (`sdks/`):
  - `python/` — `scp-memory-sdk` 0.5.0 (httpx, sync): `client.py` facade +
    `resources/{memories,intelligence,retrieval,trust}.py` + `models.py` + `_http.py`
    + `errors.py`. Injectable httpx client for in-process testing.
  - `typescript/` — `@scp/memory-sdk` 0.5.0 (Fetch API, Node 18+/browser/Deno):
    `client.ts` + `resources/*.ts` + `types.ts` + `http.ts` + `errors.ts`. Strict
    `tsc`; vitest over a stubbed fetch.
- **Deploy** (`deploy/observability/`): docker-compose stack (app + OTel collector
  + Tempo + Prometheus + Grafana), Prometheus scrape + SLO recording/alert rules,
  Grafana datasource + dashboard provisioning. Root `Dockerfile` (non-root,
  `[observability]` extra).
- **Admin Console** (`console/`, v0.6.0 — Vite + React + TS, strict modularity,
  largest file 233 lines): `src/theme/` (design tokens — Inter, 8-pt grid,
  light+dark), `src/state/settings.tsx` (namespace/baseUrl/actor/theme, persisted),
  `src/api/` (`client.ts`, `queries.ts`, `mutations.ts` over `@scp/memory-sdk`;
  `metrics.ts` pure Prometheus parser + quantiles), `src/components/` (States,
  Badge, ScoreBar, Sidebar, PageHead), `src/screens/` (Dashboard, MemoryExplorer +
  MemoryDetail, RetrievalInspector, TrustExplorer, Benchmarks, Settings). Same-origin
  transport (Vite dev proxy / reverse proxy in prod). Reuses the built SDK via
  `file:../sdks/typescript`.
- **Tests:** Python **105 passing** (+1 benchmark). TypeScript SDK **6 passing**.
  Console **8 passing** (Prometheus parser + quantile/error-ratio math; UI-primitive
  rendering) — `tsc` strict typecheck clean; production build green (~74 kB gzip).
- **Docs/examples:** `docs/phase-1..6-*.md`, `examples/quickstart.py`,
  `examples/intelligence_quickstart.py`, `examples/retrieval_quickstart.py`,
  `examples/trust_quickstart.py`, `examples/sdk_quickstart.py`.

## Quality Gates (Phase 7) — all met

Inspectable UI over all signals (6 screens) · explainability made visual
(score-bar primitive) · required Empty/Loading/Error/keyboard/a11y states · design
system (Inter, 8-pt grid, light+dark) · SDK reuse (no engine change) · `tsc` strict
clean · 8 console tests green · production build green. Strict modularity preserved
(largest console file 233 lines; none > 300). Live data contracts verified against
a running engine.

## What Does NOT Exist Yet

- **Real semantic embeddings on the default path** — the default `HashingEmbedder`
  remains the hermetic stand-in. A real offline model now exists
  (`SCP_EMBEDDER=sentence-transformers`, ADR-011) but is opt-in (needs the
  `[embeddings]` extra) so CI stays offline-by-default.
- **Qdrant in CI** — the adapter is wired behind `SCP_VECTOR_BACKEND=qdrant` but is
  integration-only; the tested default is the in-process brute-force backend.
- **Semantic trust** — corroboration/contradiction are **lexical stand-ins**
  (token overlap + negation polarity); real NLI swaps in behind `trust_service`.
  Trust **calibration** (predicted vs. observed correctness) not yet measured.
- **SDK publishing** — packaging is ready (hatchling wheel + `tsc` build) but not
  pushed to PyPI / npm; Python async client deferred.
- **Tracing on the default path** — tracing is opt-in (`SCP_TRACING_ENABLED` +
  `[observability]` extra) so CI/offline dev stay free of OpenTelemetry. Per-stage
  retrieval spans and Tempo-on-object-storage are deferred to prod hardening.
- **Console auth/session** — the console trusts the network boundary today; no login
  layer. Multi-origin/hosted console (opt-in CORS) and historical trend charts deferred.
- Android app — Phase 8.

## Next Step

**Phase 8 — Android Reference App** (on-device semantic memory demo against the
engine). Begin **only after explicit approval** (see
[08-active-phase](08-active-phase.md)).

## Pointers

- Active phase & stop rule: [08-active-phase](08-active-phase.md)
- Handoff for next session: [28-session-handoff](28-session-handoff.md)
- Backlog: [09-backlog](09-backlog.md) · Roadmap: [23-roadmap](23-roadmap.md)
- Phase guides: [../docs/phase-1-memory-core.md](../docs/phase-1-memory-core.md) ·
  [../docs/phase-2-memory-intelligence.md](../docs/phase-2-memory-intelligence.md) ·
  [../docs/phase-3-hybrid-retrieval.md](../docs/phase-3-hybrid-retrieval.md) ·
  [../docs/phase-4-trust-layer.md](../docs/phase-4-trust-layer.md) ·
  [../docs/phase-5-sdks.md](../docs/phase-5-sdks.md) ·
  [../docs/phase-6-observability.md](../docs/phase-6-observability.md) ·
  [../docs/phase-7-admin-console.md](../docs/phase-7-admin-console.md)
