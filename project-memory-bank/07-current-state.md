# 07 — Current State

**Last updated:** 2026-06-20 · **Read this first, every session.**

> Doubles as the project's **implementation-status** save state (05 working
> agreement): update on every major feature / phase boundary.

## Snapshot

- **Phase:** 2 — Memory Intelligence **complete** (pending approval to start Phase 3).
- **Repository:** `scp-memory-core`, branch `master`. Python package, tests, CI,
  docs, examples, and the memory bank.
- **Application code:** Memory Core (Phase 1) **plus** the intelligence layer:
  importance scoring, deduplication, consolidation, decay.
- **Memory bank:** all 29 files (`00`–`28`) current.
- **Version:** 0.2.0.

## What Exists (code)

- **Package** `src/scp_memory/` (src layout, strict modularity — longest file
  192 lines, all < 300):
  - `models/` — `Memory` (now with `importance` + `access_count`), `Provenance`,
    `AuditEvent`, `MemoryRelation` (now written to), enums, id helpers.
  - `intelligence/` — `scoring.py` (pure importance math), `similarity.py` (pure
    lexical Jaccard).
  - `services/` — `memory_service`, `audit_service`, `importance_service`,
    `dedup_service`, `consolidation_service`, `decay_service`, `relation_service`.
  - `api/` — FastAPI factory, routes (`/v1/memories` CRUD + `/audit`,
    `/v1/intelligence/{decay,dedup,consolidate}`, `/health`, `/metrics`).
  - `db/`, `config.py` (+ decay/dedup thresholds), `logging_config.py`,
    `metrics.py` (+ decay/dedup/consolidate counters).
- **Tests** (`tests/`): unit (pure logic + each service) + integration +
  benchmark seed — **46 passing** (+1 benchmark).
- **Docs/examples:** `docs/phase-1-memory-core.md`,
  `docs/phase-2-memory-intelligence.md`, `examples/quickstart.py`,
  `examples/intelligence_quickstart.py`.

## Quality Gates (Phase 2) — all met

API defined · tests (unit/integration/benchmark) · logging · metrics · docs ·
example. Lint + format clean. Strict modularity preserved.

## What Does NOT Exist Yet

- Retrieval (keyword/vector/metadata + ranking) — **Phase 3**. Importance is
  computed but not yet consumed by a ranking engine.
- Semantic (embedding) similarity — Phase 3 (current dedup is lexical).
- Trust runtime, SDKs, console, Android app — Phases 4–8.

## Next Step

**Phase 3 — Hybrid Retrieval.** Begin **only after explicit approval**
(see [08-active-phase](08-active-phase.md)).

## Pointers

- Active phase & stop rule: [08-active-phase](08-active-phase.md)
- Handoff for next session: [28-session-handoff](28-session-handoff.md)
- Backlog: [09-backlog](09-backlog.md) · Roadmap: [23-roadmap](23-roadmap.md)
- Phase guides: [../docs/phase-1-memory-core.md](../docs/phase-1-memory-core.md) ·
  [../docs/phase-2-memory-intelligence.md](../docs/phase-2-memory-intelligence.md)
