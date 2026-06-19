# 07 — Current State

**Last updated:** 2026-06-20 · **Read this first, every session.**

## Snapshot

- **Phase:** 0 — Project Foundation (in progress → effectively complete this session)
- **Repository:** `scp-memory-core`, branch `master`. Contains `LICENSE`,
  `README.md`, and the `project-memory-bank/`.
- **Application code:** **none yet.** No Python package, no API, no stores.
- **Memory bank:** fully scaffolded — all 29 files (`00`–`28`) populated with
  real Phase 0 content.

## What Exists

- Full memory bank (this directory).
- Locked technology stack, recorded as **Accepted** ADRs ([25-adr-log](25-adr-log.md)),
  with narrative in [06-technical-decisions](06-technical-decisions.md):
  Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.x, SQLite→Postgres, Qdrant,
  NetworkX, OpenTelemetry/Prometheus/Grafana, Pytest.
- Design intent for architecture, domain, retrieval, ranking, trust, security,
  observability, testing, and UI.

## What Does NOT Exist Yet

- Any executable code or project skeleton (pyproject, package layout).
- Storage layer, CRUD APIs, audit trail (those are **Phase 1**).
- Retrieval, intelligence, trust runtime, SDKs, console, Android app.

## Next Step

**Phase 1 — Memory Core** (Memory entity model, storage layer, CRUD APIs, audit
trail). Begin **only after explicit approval** (see [08-active-phase](08-active-phase.md)).

## Pointers

- Active phase & stop rule: [08-active-phase](08-active-phase.md)
- Handoff for next session: [28-session-handoff](28-session-handoff.md)
- Backlog: [09-backlog](09-backlog.md) · Roadmap: [23-roadmap](23-roadmap.md)
