# 04 — Domain Model

**Status:** Active · **Phase:** 0 (design intent) · **Last updated:** 2026-06-20

The shared vocabulary of the system. Concrete schemas are defined in
[11-data-models](11-data-models.md); per-area detail in the model files (12–15).
This is conceptual and stable across phases.

## Core Entities

### Memory
The central entity. A unit of remembered information.
- `id`, `content`, `type` (e.g., fact, event, preference, summary)
- `created_at`, `updated_at`, `last_accessed_at`
- `importance` (derived, Phase 2)
- `state` (active / consolidated / decayed / archived / deleted)
- `metadata` (arbitrary tags, namespace/owner, source)
- Links to: Provenance, Embedding, TrustSignals, AuditEvents

### Provenance
Where a memory came from and how it was derived.
- `source` (user, agent, document, system)
- `derivation` (raw / summarized / consolidated-from[…])
- `actor` (who/what created it)

### Importance
A derived score (Phase 2) influencing retention and ranking.
- `score`, `factors` (recency, frequency, explicit signals)

### Embedding
Vector representation for semantic retrieval (lives in the vector store).
- `vector`, `model`, `dim`, `memory_id`

### RetrievalQuery
A request for memories.
- `query_text`, `filters` (metadata), `k`, `mode` (keyword/vector/hybrid)

### RankingResult
A scored, ordered retrieval result.
- `memory_id`, `score`, `signals` (keyword score, vector score, metadata match,
  trust contribution) — signals make ranking explainable.

### TrustSignal
First-class trust dimensions attached to results (Phase 4).
- `provenance_quality`, `confidence`, `freshness`, `explanation`

### AuditEvent
Append-only record of every mutation.
- `id`, `memory_id`, `action`, `actor`, `timestamp`, `before/after` (or diff)

## Relationships

```
Memory 1───* AuditEvent
Memory 1───1 Provenance
Memory 1───1 Importance        (Phase 2)
Memory 1───1 Embedding         (Phase 3, in vector store)
Memory *───* Memory            (graph relations, NetworkX)
RetrievalQuery 1───* RankingResult ───* TrustSignal  (Phase 3–4)
Memory *───1 Consolidation     (a consolidated memory derives from many)
```

## Lifecycle (summary)

`created → (scored, deduped) → active → consolidated/decayed → archived → deleted`

Detail in [12-memory-model](12-memory-model.md).

## Related

[11-data-models](11-data-models.md) · [12-memory-model](12-memory-model.md) · [15-trust-model](15-trust-model.md) · [03-system-architecture](03-system-architecture.md)
