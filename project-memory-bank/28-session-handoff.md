# 28 — Session Handoff

**Last updated:** 2026-06-20 · **Read this first, every session.**

## Last Session Summary

**Date:** 2026-06-20
**Goal:** Implement Phase 3 — Hybrid Retrieval (keyword + vector + metadata +
ranking fusion).

### What was done
- **Embeddings:** `retrieval/embedding.py` — deterministic, dependency-free
  `HashingEmbedder` (feature-hashing → L2-normalized vector) + `cosine_similarity`,
  behind an `Embedder` protocol. Pure.
- **Keyword:** `retrieval/keyword.py` — pure Okapi BM25 over the candidate corpus.
- **Fusion:** `retrieval/fusion.py` — `weighted_fuse` (default, explainable) +
  `reciprocal_rank_fusion`; min-max `normalize`.
- **Vector backends:** `services/vector_backend.py` — `VectorBackend` protocol +
  `BruteForceBackend` (default) + cached `get_backend()`. `services/qdrant_backend.py`
  — optional ANN adapter + `reindex`, lazily imported, integration-only.
- **Orchestration:** `services/retrieval_service.py` — metadata filter → keyword ∪
  vector candidates → fuse → rank → top-k; touches returned hits (feeds Phase-2
  importance/decay).
- **API:** `POST /v1/retrieval/search` returns explainable results (per-signal
  scores + weights). `schemas/retrieval.py`, `api/routes/retrieval.py`.
- **Wiring:** config (`vector_backend`, `qdrant_url`, `qdrant_collection`), metrics
  (`RETRIEVAL_QUERIES`), app router + version, `[vector]` optional extra.
- **Tests:** 70 passing (pure unit: embedding/keyword/fusion; service; integration);
  ruff + black clean. Docs `phase-3-hybrid-retrieval.md` +
  `examples/retrieval_quickstart.py` (verified end-to-end).

### Decisions / notes
- `HashingEmbedder` is a **deterministic stand-in** (similarity ≈ shared tokens,
  not meaning); a real model swaps in behind the `Embedder` protocol.
- Qdrant adapter is wired but **integration-only / not in CI**; brute-force is the
  tested default. `qdrant-client` lives in the optional `[vector]` extra.
- Default fusion = weighted-linear; keyword/vector normalized per result set.
- Retrieval **touches** returned top-k (mutates on read) per 13-retrieval-model.
- Version → 0.3.0. No DB migrations introduced this phase.

### State
- Phase 3 **complete**, pending confirmation. No commit made yet (Phases 1–3
  all uncommitted on `master`).

## Where to Resume

**Next:** Phase 4 — Trust Layer (provenance quality, confidence, freshness,
explainability). See [09-backlog](09-backlog.md) Phase 4 section.

> **Do not start Phase 4 without explicit approval** ([08-active-phase](08-active-phase.md)).

## First Actions Next Session
1. Read `07`, `08`, `28` (this file).
2. Confirm Phase 3 acceptance / get approval to begin Phase 4.
3. If approved, follow the Phase 4 backlog with all quality gates.

## Open Questions for User
- Approve Phase 3 and authorize Phase 4?
- Commit the Phases 1–3 code now? (nothing has been committed yet)
- For production semantics: which embedding model (local sentence-transformers vs.
  a hosted API) should the `Embedder` seam target?

## Related

[07-current-state](07-current-state.md) · [08-active-phase](08-active-phase.md) · [09-backlog](09-backlog.md)
