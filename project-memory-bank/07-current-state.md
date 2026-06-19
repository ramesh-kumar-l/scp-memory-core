# 07 — Current State

**Last updated:** 2026-06-20 · **Read this first, every session.**

> Doubles as the project's **implementation-status** save state (05 working
> agreement): update on every major feature / phase boundary.

## Snapshot

- **Phase:** 1 — Memory Core **complete** (pending approval to start Phase 2).
- **Repository:** `scp-memory-core`, branch `master`. Now contains the Python
  package, tests, CI, docs, and examples in addition to the memory bank.
- **Application code:** **Memory Core shipped.** Durable, audited, namespaced
  CRUD over memories, behind a FastAPI surface.
- **Memory bank:** all 29 files (`00`–`28`) current.

## What Exists (code)

- **Package** `src/scp_memory/` (src layout, strict modularity — every file
  < 300 lines):
  - `models/` — `Memory`, `Provenance`, `AuditEvent`, `MemoryRelation`
    (table only), enums, id helpers.
  - `services/` — `memory_service` (CRUD + namespacing), `audit_service`
    (append-only, atomic with mutations).
  - `api/` — FastAPI app factory, routes (`/v1/memories` CRUD + `/audit`,
    `/health`, `/metrics`), problem-shape errors, observability middleware.
  - `db/`, `config.py`, `logging_config.py` (JSON, no content), `metrics.py`
    (Prometheus).
- **Tests** (`tests/`): unit + integration + benchmark seed — **18 passing**.
- **Tooling:** `pyproject.toml` (hatchling, ruff, black, pytest), GitHub Actions
  CI (lint + format + tests on 3.11/3.12).
- **Docs/examples:** `docs/phase-1-memory-core.md`, `examples/quickstart.py`.

## Quality Gates (Phase 1) — all met

API defined · tests (unit/integration/benchmark) · logging · metrics · docs ·
benchmark seed · examples. Lint + format clean.

## What Does NOT Exist Yet

- Intelligence (importance/dedup/consolidation/decay) — **Phase 2**.
- Retrieval (keyword/vector/metadata + ranking) — **Phase 3**.
- Trust runtime, SDKs, console, Android app — Phases 4–8.
- `memory_relations` has no write paths yet (table defined for Phase 2).

## Next Step

**Phase 2 — Memory Intelligence.** Begin **only after explicit approval**
(see [08-active-phase](08-active-phase.md)).

## Pointers

- Active phase & stop rule: [08-active-phase](08-active-phase.md)
- Handoff for next session: [28-session-handoff](28-session-handoff.md)
- Backlog: [09-backlog](09-backlog.md) · Roadmap: [23-roadmap](23-roadmap.md)
- Phase 1 dev guide: [../docs/phase-1-memory-core.md](../docs/phase-1-memory-core.md)
