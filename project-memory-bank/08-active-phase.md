# 08 — Active Phase

**Last updated:** 2026-06-20 · **Read this first, every session.**

> Doubles as the project's **active-context** save state (05 working agreement).

## Active Phase: 2 — Memory Intelligence ✅ complete (awaiting approval for Phase 3)

### Goal
Memory that manages itself: importance scoring, deduplication, consolidation,
and decay — the self-management layer over Phase 1's audited CRUD.

### Deliverables
- [x] Importance scoring (recency + frequency + explicit signal → `importance` in [0,1])
- [x] Deduplication (lexical Jaccard; archive non-canonical + `supersedes` edges)
- [x] Consolidation (summary memory + `derived_from` edges; sources → `consolidated`)
- [x] Decay (recompute over namespace; below-threshold `active` → `decayed`)
- [x] First `memory_relations` write paths (`relation_service`)
- [x] Intelligence API (`/v1/intelligence/decay|dedup|consolidate`); importance on every read
- [x] Tests (unit pure-logic + per-service + integration), metrics, logging, docs, example

### Exit Criteria (all met)
- 46 tests passing (+ benchmark seed); ruff + black clean.
- Every transition audited; provenance preserved; lifecycle states honoured.
- Strict modularity: longest source file 192 lines (none > 300).
- Quality gates satisfied ([05-engineering-principles](05-engineering-principles.md)).

### Status
**Complete** (pending user confirmation). Awaiting approval to start Phase 3.

### Key decisions
- Similarity is **lexical** (token-set Jaccard) in Phase 2; semantic/embedding
  dedup arrives with the vector store in Phase 3. Merge logic is scorer-agnostic.
- New `Memory.access_count` column feeds the frequency signal.
- `GET /v1/memories` default now returns **active only**; lifecycle by-products
  reachable via explicit `state` filter.
- Added `AuditAction.deduplicate`. Version bumped 0.1.0 → 0.2.0.

---

## ⛔ Stop Rule (operating model)

> One phase is active at a time. **Do NOT begin Phase 3 (Hybrid Retrieval)
> without explicit user approval.** Never work ahead or skip phases.

At the end of any phase: update `07`, `08`, `28`, then **stop** and wait for
explicit instruction.

## Next Phase (do not start yet)

**Phase 3 — Hybrid Retrieval:** keyword + vector (Qdrant) + metadata retrieval and
a ranking engine that consumes the `importance` signal produced here. Scoped in
[09-backlog](09-backlog.md).

## Related

[07-current-state](07-current-state.md) · [28-session-handoff](28-session-handoff.md) · [23-roadmap](23-roadmap.md)
