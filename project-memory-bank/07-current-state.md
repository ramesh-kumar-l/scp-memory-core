# 07 — Current State

**Last updated:** 2026-06-20 · **Read this first, every session.**

> Doubles as the project's **implementation-status** save state (05 working
> agreement): update on every major feature / phase boundary.

## Snapshot

- **Phase:** 8 — Android Reference App **in progress** (user-approved 2026-06-20).
  Phases 1–7 complete. The Android app lives in a **separate** folder,
  `E:\ClaudeProjects\SCPMemoryEngine—AndroidReferenceApp`; engine code here is
  unchanged by it. See [08-active-phase](08-active-phase.md) for the Phase-8 detail.
- **Repository:** `scp-memory-core`, branch `master`. Python package, two client
  SDKs, an observability deploy stack, an **admin console SPA**, tests, CI, docs,
  examples, and the memory bank.
- **Application code:** Memory Core (Phase 1) + Intelligence (Phase 2) + Hybrid
  Retrieval (Phase 3) + Trust Layer (Phase 4) + SDKs (Phase 5) + Observability
  (Phase 6). Phase 7 adds the **Admin Console** (`console/`): a Vite + React + TS
  SPA over the full signal surface — Dashboard, Memory Explorer, Retrieval
  Inspector, Trust Explorer, Benchmarks, Settings — reusing `@scp/memory-sdk` and
  talking to the engine same-origin (no CORS / no engine change).
- **Memory bank:** all 29 files (`00`–`28`) current, plus two Phase-8 **prep
  artifacts**: `29-api-contracts.md` (consolidated *implemented* HTTP surface) and
  `android-app-system-prompt.md` (self-contained Android Reference App spec for a
  separate Claude Design session). These are specs only — **no Phase-8 code**.
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
- **Production-hardening (post-Phase-7, specs→code, all gated paths opt-in):**
  - `trust/relation.py` + `services/relation_detector.py` — corroboration detection
    behind a `RelationDetector` seam; **lexical default**, **NLI opt-in**
    (`SCP_TRUST_NLI`, cross-encoder, on-device, fails loud without `[embeddings]`).
  - `services/keyword_backend.py` (+ `fts5_backend.py`, `tsvector_backend.py`) —
    keyword search behind a backend seam; **in-process BM25 default**, **SQLite
    FTS5** and **Postgres tsvector** inverted-index scale paths (`SCP_KEYWORD_BACKEND`).
  - `retrieval/fusion.rrf_fuse` + `retrieval_service.search(fuse_method=…)` — RRF
    selectable alongside weighted (internal/benchmark knob; API unchanged).
  - `observability/spans.py` — no-op-safe per-stage retrieval spans
    (candidates/vector/keyword/trust/fuse).
  - `evals/` — offline harnesses: trust **calibration** (Brier/ECE) and **weighted-
    vs-RRF** retrieval benchmark (nDCG/MRR) over fixed labelled datasets.
  - `deploy/observability/alertmanager/` + Prometheus `alerting:` — severity-routed
    alerts (page/ticket) with engine-down inhibition.
  - CI `integration` job (Postgres + Qdrant services) + env-gated tests.
- **Tests:** Python **132 passing** (+1 benchmark; +3 **gated** Postgres/Qdrant
  integration tests, skipped offline). TypeScript SDK **6 passing**. Console
  **8 passing** — `tsc` strict typecheck clean; production build green (~74 kB gzip).
  Lint (`ruff`) + format (`black`) clean across `src tests evals`.
- **Docs/examples:** `docs/phase-1..6-*.md`, `examples/quickstart.py`,
  `examples/intelligence_quickstart.py`, `examples/retrieval_quickstart.py`,
  `examples/trust_quickstart.py`, `examples/sdk_quickstart.py`.
- **Leverage artifacts (2026-06-21, docs/distribution layer — NOT a new engine phase;
  engine `src/` unchanged):** `documents/` (18 files: project analysis → Pareto → 80/20
  set → engineering thesis, architecture doc, ADR collection, README positioning,
  benchmark report, principal case study, blog plan, demo pack, talk deck, roadmap,
  reusable-asset catalog, career + startup leverage, 30-day plan) + `documents/golden-examples.json`
  (10 Golden Examples, single source of truth). `seed/seed_golden_examples.py`
  (+`seed/README.md`) seeds the engine over the HTTP API (validated in-process: 10/10
  created, trust-scored search verified); the Android repo gains `seed/seed_golden_device.py`
  (direct Room write, backdated ages, `--reset`) consuming the same JSON. Root
  `Quick_Stater_Guide.md` (newbie zero-to-run) and `blog_series/` (7 publish-ready posts
  with mermaid). Framing: Principal-level / FAANG-visibility.

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
- **Qdrant / Postgres in CI** — now exercised by a dedicated `integration` CI job
  (services: postgres 16 + qdrant) with env-gated tests; **locally these skip**
  (no services). The offline default remains brute-force + SQLite.
- **Semantic trust** — corroboration/contradiction default to **lexical stand-ins**;
  a real **NLI detector is now available opt-in** (`SCP_TRUST_NLI`). The
  lexical→NLI swap is **gated on the calibration harness**
  (`evals/run_trust_calibration.py`): on the fixed set the lexical detector scores
  Brier ≈ 0.17 / ECE ≈ 0.19, with visible over-confidence where it mis-reads
  semantic contradictions (dark/light, berlin/munich) — turn NLI on only when it
  measurably lowers ECE. NLI not yet run in CI (needs the `[embeddings]` model).
- **FTS5/tsvector in production** — backends exist and FTS5 is unit-tested; the
  default keyword path stays in-process BM25. tsvector is exercised only in the
  Postgres CI job.
- **SDK publishing** — packaging ready (hatchling wheel + `tsc` build) but **not
  pushed** to PyPI / npm; **async Python client deferred**. Step-by-step runbook
  now in [Publish_Guide](Publish_Guide.md).
- **Tracing on the default path** — tracing stays opt-in (`SCP_TRACING_ENABLED` +
  `[observability]` extra) so CI/offline dev stay free of OpenTelemetry. **Per-stage
  retrieval spans now exist** (`observability/spans.py`, no-op-safe) and activate
  when tracing is enabled. Tempo-on-object-storage remains deferred.
- **Console auth/session** — the console trusts the network boundary today; no login
  layer. Multi-origin/hosted console (opt-in CORS) and historical trend charts deferred.
- **Android app — Phase 8 (in progress, separate repo).** Built per
  `android-app-system-prompt.md`: Compose/M3/MVVM/Hilt/Room/Retrofit, **hybrid**
  (live engine or local seeded store), 6 screens, 3 Golden Use Cases, PC seed/reset
  scripts that write the device Room DB directly via `adb run-as`. 74 Kotlin files,
  all < 300 lines. **Not yet build/run-verified on a device**; Gradle wrapper jar is
  generated by Android Studio on first open (not committed). Engine code here is
  untouched.

## Next Step

**Phase 8 — Android Reference App:** continue in
`SCPMemoryEngine—AndroidReferenceApp`. Remaining: device build/run verification,
optional ViewModel tests, optional Inter font + inline-edit UI. Engine repo
`scp-memory-core` needs no further work for Phase 8.

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
