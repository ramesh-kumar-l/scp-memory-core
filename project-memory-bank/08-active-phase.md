# 08 — Active Phase

**Last updated:** 2026-06-20 · **Read this first, every session.**

> Doubles as the project's **active-context** save state (05 working agreement).

## Active Phase: 1 — Memory Core ✅ complete (awaiting approval for Phase 2)

### Goal
Durable, auditable CRUD over memories — the foundation every later phase extends.

### Deliverables
- [x] Project skeleton: pyproject, src layout, ruff/black/pytest, CI
- [x] SQLAlchemy models: `memories`, `provenance`, `audit_events`, `memory_relations`
- [x] Memory service: create/read/update/delete with namespacing
- [x] Audit trail: append-only event emitted atomically on every mutation
- [x] FastAPI endpoints for CRUD + `/{id}/audit` (+ `/health`, `/metrics`)
- [x] Tests (unit + integration + benchmark seed), metrics, logging, docs, examples

### Exit Criteria (all met)
- 18 tests passing; ruff + black clean.
- Every mutation audited; provenance always recorded; soft/hard delete governed.
- Quality gates satisfied ([05-engineering-principles](05-engineering-principles.md)).

### Status
**Complete** (pending user confirmation). Awaiting approval to start Phase 2.

---

## ⛔ Stop Rule (operating model)

> One phase is active at a time. **Do NOT begin Phase 2 (Memory Intelligence)
> without explicit user approval.** Never work ahead or skip phases.

At the end of any phase: update `07`, `08`, `28`, then **stop** and wait for
explicit instruction.

## Next Phase (do not start yet)

**Phase 2 — Memory Intelligence:** importance scoring, deduplication,
consolidation, decay. Scoped in [09-backlog](09-backlog.md). All quality gates
apply. Builds on the `memory_relations` table and lifecycle states already
defined in Phase 1.

## Related

[07-current-state](07-current-state.md) · [28-session-handoff](28-session-handoff.md) · [23-roadmap](23-roadmap.md)
