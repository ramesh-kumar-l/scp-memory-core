# 07 — Current State

**Last updated:** 2026-06-20 · **Read this first, every session.**

> Doubles as the project's **implementation-status** save state (05 working
> agreement): update on every major feature / phase boundary.

## Snapshot

- **Phase:** 5 — SDKs **complete** (pending approval to start Phase 6).
- **Repository:** `scp-memory-core`, branch `master`. Python package, two client
  SDKs, tests, CI, docs, examples, and the memory bank.
- **Application code:** Memory Core (Phase 1) + Intelligence (Phase 2) + Hybrid
  Retrieval (Phase 3) + Trust Layer (Phase 4). Phase 5 adds **Python + TypeScript
  SDKs** covering the full API, plus a real **offline local embedder**
  (sentence-transformers `all-MiniLM-L6-v2`) behind the existing `Embedder` seam.
- **Memory bank:** all 29 files (`00`–`28`) current.
- **Version:** engine 0.4.0; SDKs 0.5.0.

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
    `/v1/trust/{memory_id}`, `/health`, `/metrics`).
  - `db/`, `config.py` (+ vector-backend/Qdrant settings), `logging_config.py`,
    `metrics.py` (+ retrieval & trust counters).
- **SDKs** (`sdks/`):
  - `python/` — `scp-memory-sdk` 0.5.0 (httpx, sync): `client.py` facade +
    `resources/{memories,intelligence,retrieval,trust}.py` + `models.py` + `_http.py`
    + `errors.py`. Injectable httpx client for in-process testing.
  - `typescript/` — `@scp/memory-sdk` 0.5.0 (Fetch API, Node 18+/browser/Deno):
    `client.ts` + `resources/*.ts` + `types.ts` + `http.ts` + `errors.ts`. Strict
    `tsc`; vitest over a stubbed fetch.
- **Tests:** Python **96 passing** (+1 benchmark) — adds 4 embedder-factory + 6 SDK
  round-trip (CRUD/audit/retrieval-with-trust/trust/consolidate) via `TestClient`.
  TypeScript **6 passing** (typecheck + build clean).
- **Docs/examples:** `docs/phase-1..5-*.md`, `examples/quickstart.py`,
  `examples/intelligence_quickstart.py`, `examples/retrieval_quickstart.py`,
  `examples/trust_quickstart.py`, `examples/sdk_quickstart.py`.

## Quality Gates (Phase 5) — all met

Full-surface clients defined · tests (Python round-trip in-process + TS vitest) ·
logging · metrics · docs · example. Python ruff + black clean; TS `tsc --noEmit`
clean. Strict modularity preserved (longest new file 208, SDK `models.py`).

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
- Console, Android app — Phases 7–8.

## Next Step

**Phase 6 — Observability** (Prometheus/Grafana dashboards, OTel tracing, SLOs).
Begin **only after explicit approval** (see [08-active-phase](08-active-phase.md)).

## Pointers

- Active phase & stop rule: [08-active-phase](08-active-phase.md)
- Handoff for next session: [28-session-handoff](28-session-handoff.md)
- Backlog: [09-backlog](09-backlog.md) · Roadmap: [23-roadmap](23-roadmap.md)
- Phase guides: [../docs/phase-1-memory-core.md](../docs/phase-1-memory-core.md) ·
  [../docs/phase-2-memory-intelligence.md](../docs/phase-2-memory-intelligence.md) ·
  [../docs/phase-3-hybrid-retrieval.md](../docs/phase-3-hybrid-retrieval.md) ·
  [../docs/phase-4-trust-layer.md](../docs/phase-4-trust-layer.md) ·
  [../docs/phase-5-sdks.md](../docs/phase-5-sdks.md)
