# 07 — Current State

**Last updated:** 2026-06-20 · **Read this first, every session.**

> Doubles as the project's **implementation-status** save state (05 working
> agreement): update on every major feature / phase boundary.

## Snapshot

- **Phase:** 3 — Hybrid Retrieval **complete** (pending approval to start Phase 4).
- **Repository:** `scp-memory-core`, branch `master`. Python package, tests, CI,
  docs, examples, and the memory bank.
- **Application code:** Memory Core (Phase 1) + Intelligence (Phase 2) + Hybrid
  Retrieval (Phase 3): keyword (BM25) + vector + metadata + ranking fusion.
- **Memory bank:** all 29 files (`00`–`28`) current.
- **Version:** 0.3.0.

## What Exists (code)

- **Package** `src/scp_memory/` (src layout, strict modularity — all files < 300
  lines; longest 192):
  - `models/` — `Memory` (with `importance` + `access_count`), `Provenance`,
    `AuditEvent`, `MemoryRelation`, enums, id helpers.
  - `intelligence/` — `scoring.py` (importance), `similarity.py` (lexical Jaccard).
  - `retrieval/` — `embedding.py` (`HashingEmbedder` + cosine, pure), `keyword.py`
    (BM25, pure), `fusion.py` (weighted + RRF, pure), `config.py`.
  - `services/` — `memory_service`, `audit_service`, `importance_service`,
    `dedup_service`, `consolidation_service`, `decay_service`, `relation_service`,
    `retrieval_service`, `vector_backend` (brute-force default), `qdrant_backend`
    (optional, integration-only).
  - `api/` — FastAPI factory, routes (`/v1/memories` CRUD + `/audit`,
    `/v1/intelligence/{decay,dedup,consolidate}`, `/v1/retrieval/search`,
    `/health`, `/metrics`).
  - `db/`, `config.py` (+ vector-backend/Qdrant settings), `logging_config.py`,
    `metrics.py` (+ retrieval counter).
- **Tests** (`tests/`): unit (pure logic + each service) + integration +
  benchmark seed — **70 passing** (+1 benchmark).
- **Docs/examples:** `docs/phase-1..3-*.md`, `examples/quickstart.py`,
  `examples/intelligence_quickstart.py`, `examples/retrieval_quickstart.py`.

## Quality Gates (Phase 3) — all met

API defined · tests (unit/integration/benchmark) · logging · metrics · docs ·
example. Lint + format clean. Strict modularity preserved (longest new file 134).

## What Does NOT Exist Yet

- **Real semantic embeddings** — the default `HashingEmbedder` is a deterministic
  token-hash stand-in (similarity ≈ shared tokens, not meaning). A real model
  drops in behind the `Embedder` protocol.
- **Qdrant in CI** — the adapter is wired behind `SCP_VECTOR_BACKEND=qdrant` but is
  integration-only; the tested default is the in-process brute-force backend.
- Trust runtime, SDKs, console, Android app — Phases 4–8.

## Next Step

**Phase 4 — Trust Layer.** Begin **only after explicit approval**
(see [08-active-phase](08-active-phase.md)).

## Pointers

- Active phase & stop rule: [08-active-phase](08-active-phase.md)
- Handoff for next session: [28-session-handoff](28-session-handoff.md)
- Backlog: [09-backlog](09-backlog.md) · Roadmap: [23-roadmap](23-roadmap.md)
- Phase guides: [../docs/phase-1-memory-core.md](../docs/phase-1-memory-core.md) ·
  [../docs/phase-2-memory-intelligence.md](../docs/phase-2-memory-intelligence.md) ·
  [../docs/phase-3-hybrid-retrieval.md](../docs/phase-3-hybrid-retrieval.md)
