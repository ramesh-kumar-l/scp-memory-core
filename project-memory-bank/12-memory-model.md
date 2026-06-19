# 12 — Memory Model

**Status:** Design intent · **Primary target:** Phase 1 (entity) + Phase 2 (lifecycle) · **Last updated:** 2026-06-20

Defines the Memory entity, its states, and lifecycle. Schema in
[11-data-models](11-data-models.md); concepts in [04-domain-model](04-domain-model.md).

## What is a Memory?

A durable unit of remembered information with content, a type, provenance, and a
lifecycle state. Memories are scoped by `namespace` (tenant/owner).

## Types (open set)

- `fact` — stable knowledge ("user's timezone is IST")
- `event` — something that happened ("user upgraded plan on 2026-06-01")
- `preference` — a stated/inferred preference ("prefers concise answers")
- `summary` — condensed/consolidated memory derived from others

## States & Lifecycle

```
created ──score/dedup──▶ active ──consolidate──▶ consolidated
                          │                          │
                          ├──────────decay──────────▶ decayed
                          │                              │
                          └──────────archive────────▶ archived ──▶ deleted
```

- **created:** just written; importance not yet scored.
- **active:** live and retrievable.
- **consolidated:** merged into/derived as a summary memory (Phase 2).
- **decayed:** importance fell below threshold; deprioritized, retained for audit.
- **archived:** removed from default retrieval; recoverable.
- **deleted:** governed removal; audit retained.

## Lifecycle Operations (Phase 2)

- **Importance scoring** — recency + frequency + explicit signals → `importance`.
  See [14-ranking-model](14-ranking-model.md) for how importance feeds ranking.
- **Deduplication** — detect near-duplicates (semantic + metadata) and merge.
- **Consolidation** — combine related memories into a `summary`, recording
  `derived_from` provenance.
- **Decay** — reduce importance over time; transition to `decayed` below a
  threshold.

## Invariants

- Every state transition emits an AuditEvent.
- Provenance is never lost; consolidation records source IDs.
- A memory's relational record is the source of truth; the vector point is derived.

## Phase Boundaries

- **Phase 1:** entity + states (created/active/archived/deleted) + CRUD + audit.
- **Phase 2:** importance, dedup, consolidation, decay (consolidated/decayed).

## Related

[04-domain-model](04-domain-model.md) · [11-data-models](11-data-models.md) · [13-retrieval-model](13-retrieval-model.md) · [15-trust-model](15-trust-model.md)
