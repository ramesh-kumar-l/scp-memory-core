# 08 — Active Phase

**Last updated:** 2026-06-20 · **Read this first, every session.**

> Doubles as the project's **active-context** save state (05 working agreement).

## Active Phase: 4 — Trust Layer ✅ complete (awaiting approval for Phase 5)

### Goal
Trustworthy, explainable recall: attach provenance quality, confidence
(corroboration/contradiction), and type-aware freshness to every retrieved
memory; fold a composite **trust** score into ranking; and emit a human-readable
explanation — no black boxes.

### Deliverables
- [x] Pure `trust/` package: provenance, freshness, confidence, score, explain, config
- [x] `trust_service` (DB-aware, no writes): per-memory verdict + namespace neighbours
- [x] Trust folded into ranking fusion as a 4th weighted dimension (`weights.trust`)
- [x] Results carry `signals.trust` + a full `trust` breakdown + explanation
- [x] `min_confidence` filter on search (filtered, never silently hidden)
- [x] Explain endpoint `GET /v1/trust/{memory_id}`
- [x] Tests (pure unit + service + integration), metrics, logging, docs, example

### Exit Criteria (all met)
- 86 tests passing (+ benchmark seed); ruff + black clean.
- Every result carries a decomposable trust verdict + plain-language explanation;
  namespace-isolated.
- Strict modularity: longest source file 192 lines (none > 300; longest new 162).
- Quality gates satisfied ([05-engineering-principles](05-engineering-principles.md)).

### Status
**Complete** (pending user confirmation). Awaiting approval to start Phase 5.

### Key decisions
- **Corroboration/contradiction are lexical stand-ins** (token-overlap Jaccard +
  negation-polarity divergence), mirroring the Phase-3 embedder honesty pattern —
  hermetic and swappable for semantic NLI behind `trust_service`, no contract change.
- **Confidence has a provenance floor**: corroboration closes the gap to 1.0, so a
  user-stated memory (provenance 1.0) is already at the ceiling — corroboration
  lifts *lower-provenance* memories. Contradiction subtracts a fixed penalty.
- **Freshness is type-aware** (preference 180d half-life ≫ event 14d); stale
  memories are down-weighted, never deleted.
- **Trust enters ranking as an extra weighted dimension.** Phase-4 default weights:
  keyword 0.35 / vector 0.35 / importance 0.1 / trust 0.2. `weighted_fuse` keeps
  trust optional so Phase-3 callers are unchanged.
- Version bumped 0.3.0 → 0.4.0. No DB migrations (trust reads existing columns).

---

## ⛔ Stop Rule (operating model)

> One phase is active at a time. **Do NOT begin Phase 5 (SDK) without explicit
> user approval.** Never work ahead or skip phases.

At the end of any phase: update `07`, `08`, `28`, then **stop** and wait for
explicit instruction.

## Next Phase (do not start yet)

**Phase 5 — SDK:** Python + TypeScript clients covering the full API surface
(CRUD, intelligence, retrieval, trust). Scoped in [09-backlog](09-backlog.md).

## Related

[07-current-state](07-current-state.md) · [28-session-handoff](28-session-handoff.md) · [23-roadmap](23-roadmap.md)
