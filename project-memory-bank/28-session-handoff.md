# 28 — Session Handoff

**Last updated:** 2026-06-20 · **Read this first, every session.**

## Last Session Summary

**Date:** 2026-06-20
**Goal:** Implement Phase 4 — Trust Layer (provenance quality, confidence,
freshness, explainability).

### What was done
- **Pure `trust/` package:** `provenance.py` (source→quality map), `freshness.py`
  (type-aware decay), `confidence.py` (provenance floor + corroboration boost −
  contradiction penalty), `score.py` (weighted composite), `explain.py`
  (one-sentence rationale), `config.py` (`TrustWeights`, half-lives, thresholds).
- **Orchestration:** `services/trust_service.py` — DB-aware, **no writes**. Per
  memory: provenance source, age→freshness, and corroboration/contradiction counts
  over same-type namespace neighbours (lexical: Jaccard + negation polarity).
  Pre-tokenizes the candidate set once; `evaluate` / `evaluate_all` /
  `evaluate_memory`.
- **Ranking:** `fusion.py` `weighted_fuse` gained an optional `trust` dimension
  (Phase-3 callers unchanged); `FusionWeights.trust`; retrieval default weights
  → keyword .35 / vector .35 / importance .1 / trust .2.
- **Retrieval:** `retrieval_service` computes trust for candidates, folds it into
  fusion, carries the `TrustResult` on each `RankedMemory`, applies optional
  `min_confidence` filter; eager-loads provenance (no N+1).
- **API:** search results now carry `signals.trust` + a `trust` breakdown +
  explanation; new `min_confidence` body field. New `GET /v1/trust/{memory_id}`
  explain endpoint. `schemas/retrieval.py` (`TrustBreakdown`, `trust` signal),
  `api/routes/trust.py`.
- **Wiring:** metrics `TRUST_EVALUATIONS`; app router + version 0.4.0; pyproject
  + package version.
- **Tests:** 86 passing (pure unit: signals + service; integration: explain
  endpoint, trust on results, `min_confidence` filter; updated the two Phase-3
  assertions for the new `trust` signal/weight). ruff + black clean. Docs
  `phase-4-trust-layer.md` + `examples/trust_quickstart.py` (verified end-to-end).

### Decisions / notes
- Corroboration/contradiction are **lexical stand-ins** (honest, hermetic,
  swappable for NLI behind `trust_service`). Corroboration threshold 0.5.
- Confidence has a **provenance floor**: corroboration only lifts lower-provenance
  memories (user-stated already at 1.0). Freshness is **type-aware**.
- Trust enters ranking as a weighted dimension; `weighted_fuse` keeps it optional.
- Version → 0.4.0. **No DB migrations** (trust reads existing columns).

### State
- Phase 4 **complete**, pending confirmation. No commit made yet (Phases 1–4
  all uncommitted on `master`).

## Where to Resume

**Next:** Phase 5 — SDK (Python + TypeScript clients over the full API surface,
including trust). See [09-backlog](09-backlog.md) Phase 5 section.

> **Do not start Phase 5 without explicit approval** ([08-active-phase](08-active-phase.md)).

## First Actions Next Session
1. Read `07`, `08`, `28` (this file).
2. Confirm Phase 4 acceptance / get approval to begin Phase 5.
3. If approved, follow the Phase 5 backlog with all quality gates.

## Open Questions for User
- Approve Phase 4 and authorize Phase 5?
- Commit the Phases 1–4 code now? (nothing has been committed yet)
- For production semantics: which embedding model (local sentence-transformers vs.
  a hosted API) should the `Embedder` seam target, and should trust adopt a real
  NLI model for corroboration/contradiction?

## Related

[07-current-state](07-current-state.md) · [08-active-phase](08-active-phase.md) · [09-backlog](09-backlog.md)
