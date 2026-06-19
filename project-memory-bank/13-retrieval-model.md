# 13 — Retrieval Model

**Status:** Design intent · **Primary target:** Phase 3 · **Last updated:** 2026-06-20

How memories are found. Retrieval is **hybrid**: it combines complementary
signals, then hands candidates to ranking ([14-ranking-model](14-ranking-model.md)).

## Retrieval Modes

1. **Keyword** — lexical match (e.g., BM25/FTS). Precise on exact terms,
   identifiers, rare tokens.
2. **Vector** — semantic similarity via embeddings in Qdrant. Captures meaning
   and paraphrase.
3. **Metadata** — structured filters (namespace, type, state, time ranges).
   Always applied as constraints; never returns irrelevant scopes.

**Hybrid** = metadata filter → (keyword ∪ vector) candidate generation → fuse →
rank.

## Pipeline

```
RetrievalQuery
   │
   ├─ apply metadata filters (namespace, type, state, time)
   │
   ├─ keyword candidates ─┐
   │                      ├─ candidate set (dedup by memory_id)
   ├─ vector candidates ──┘
   │
   └─ ranking ([14]) → RankingResult[] (with per-signal scores)
```

## Explainability (core requirement)

Every result carries its contributing signals: keyword score, vector score,
metadata match, and (Phase 4) trust contribution. A consumer can always answer
"why was this retrieved?" — no opaque ranking.

## Parameters

- `query`, `filters`, `k` (top-k), `mode` (keyword | vector | hybrid).
- Defaults to `hybrid`. `k` bounded to protect latency.

## Freshness & Access Effects

- Retrieval updates `last_accessed_at` (feeds importance/decay, Phase 2).
- Freshness becomes a trust signal in Phase 4 ([15-trust-model](15-trust-model.md)).

## Phase Boundaries

- **Phase 3:** keyword + vector + metadata + ranking engine.
- **Phase 4:** trust signals layered onto results.

## Open Questions

- Fusion method: weighted score vs. Reciprocal Rank Fusion — decided in Phase 3
  with benchmarks ([21-benchmark-results](21-benchmark-results.md)).
- Whether graph relations contribute candidates in Phase 3 or later.

## Related

[14-ranking-model](14-ranking-model.md) · [12-memory-model](12-memory-model.md) · [15-trust-model](15-trust-model.md) · [10-api-contracts](10-api-contracts.md)
