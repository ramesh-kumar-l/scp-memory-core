# 14 — Ranking Model

**Status:** Implemented (Phase 3 + trust in Phase 4) · **Last updated:** 2026-06-20

How retrieved candidates are scored and ordered. Ranking consumes the candidate
set from retrieval ([13-retrieval-model](13-retrieval-model.md)) and produces an
ordered, **explainable** `RankingResult[]`.

## Signals

- **Relevance**
  - `keyword_score` — lexical match strength.
  - `vector_score` — semantic similarity.
  - `metadata_match` — how well structured constraints/boosts are satisfied.
- **Memory quality**
  - `importance` — derived score (Phase 2): recency, frequency, explicit signals.
- **Trust (Phase 4)**
  - `provenance_quality`, `confidence`, `freshness` — see
    [15-trust-model](15-trust-model.md).

## Fusion

Candidate generators produce heterogeneous scores. Ranking fuses them into a
single ordering. Two candidate methods (decided in Phase 3 via benchmarks):

- **Weighted linear combination** of normalized signals (interpretable weights).
- **Reciprocal Rank Fusion (RRF)** over per-signal ranked lists (robust to scale
  differences).

Phase 3 ranks on relevance + importance. Phase 4 adds **trust** as an additional
weighted dimension (default weights: keyword 0.35 / vector 0.35 / importance 0.1 /
trust 0.2). The fused trust score is a composite of provenance/confidence/freshness
([15-trust-model](15-trust-model.md)); each result also carries the full trust
breakdown and a plain-language explanation.

## Explainability Contract

Each `RankingResult` exposes:
```json
{ "memory_id": "...", "score": 0.81,
  "signals": { "keyword": 0.3, "vector": 0.78, "metadata": 1.0,
               "importance": 0.6, "trust": 0.7 },
  "weights": { ... } }
```
A consumer can reconstruct *why* this result ranked where it did.

## Tunability

- Weights are configurable per query/profile (e.g., "favor freshness").
- Defaults chosen empirically and recorded in
  [21-benchmark-results](21-benchmark-results.md).

## Phase Boundaries

- **Phase 3:** relevance + importance fusion; explainable signals.
- **Phase 4:** trust dimensions added to the fusion.

## Related

[13-retrieval-model](13-retrieval-model.md) · [15-trust-model](15-trust-model.md) · [12-memory-model](12-memory-model.md) · [21-benchmark-results](21-benchmark-results.md)
