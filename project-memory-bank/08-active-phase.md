# 08 — Active Phase

**Last updated:** 2026-06-20 · **Read this first, every session.**

> Doubles as the project's **active-context** save state (05 working agreement).

## Active Phase: 3 — Hybrid Retrieval ✅ complete (awaiting approval for Phase 4)

### Goal
Relevant recall across signals: keyword (lexical) + vector (semantic) + metadata
retrieval, fused by a ranking engine that consumes the Phase-2 `importance`
signal — with **explainable** per-signal scores on every result.

### Deliverables
- [x] Embeddings: pure `HashingEmbedder` + cosine behind an `Embedder` protocol
- [x] Keyword retrieval: pure Okapi BM25 over metadata-filtered candidates
- [x] Vector backend seam: `BruteForceBackend` (default) + optional Qdrant adapter
- [x] Fusion: weighted-linear (default, explainable) + RRF; importance as a signal
- [x] Orchestration (`retrieval_service`): filter → keyword ∪ vector → fuse → rank
- [x] Retrieval touches returned hits (feeds Phase-2 importance/decay loop)
- [x] API (`POST /v1/retrieval/search`) with explainable signals + weights
- [x] Tests (pure unit + service + integration), metrics, logging, docs, example

### Exit Criteria (all met)
- 70 tests passing (+ benchmark seed); ruff + black clean.
- Every result is explainable (per-signal scores + weights); namespace-isolated.
- Strict modularity: longest source file 192 lines (none > 300; longest new 134).
- Quality gates satisfied ([05-engineering-principles](05-engineering-principles.md)).

### Status
**Complete** (pending user confirmation). Awaiting approval to start Phase 4.

### Key decisions
- **Embedder is a deterministic stand-in.** `HashingEmbedder` gives semantic-shaped
  vectors driven by shared tokens/hash buckets, not true meaning — chosen for
  zero-infra, hermetic, reproducible runs. A real model drops in behind the
  `Embedder` protocol with no change to retrieval/ranking.
- **Two vector backends behind one seam.** In-process brute-force is the tested
  default; Qdrant (`SCP_VECTOR_BACKEND=qdrant`, `[vector]` extra) is the
  integration-only scale path, not covered by CI.
- **Default fusion = weighted-linear** (matches the explainability contract); RRF
  available. Keyword/vector signals normalized per result set; importance absolute.
- Retrieval **mutates on read** (touch top-k) by design (13-retrieval-model).
- Version bumped 0.2.0 → 0.3.0.

---

## ⛔ Stop Rule (operating model)

> One phase is active at a time. **Do NOT begin Phase 4 (Trust Layer) without
> explicit user approval.** Never work ahead or skip phases.

At the end of any phase: update `07`, `08`, `28`, then **stop** and wait for
explicit instruction.

## Next Phase (do not start yet)

**Phase 4 — Trust Layer:** provenance quality, confidence (corroboration/
contradiction), freshness, and explainability output — layered onto the retrieval
results produced here. Scoped in [09-backlog](09-backlog.md).

## Related

[07-current-state](07-current-state.md) · [28-session-handoff](28-session-handoff.md) · [23-roadmap](23-roadmap.md)
