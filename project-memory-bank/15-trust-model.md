# 15 — Trust Model

**Status:** Design intent · **Primary target:** Phase 4 · **Last updated:** 2026-06-20

Trust is a **first-class, retrievable dimension**, not an afterthought. The trust
layer makes recall trustworthy and explainable. It augments ranking
([14-ranking-model](14-ranking-model.md)) and travels with every result.

## Trust Signals

1. **Provenance** — where the memory came from and how it was derived
   (user-stated > inferred; raw source recorded; consolidation keeps source IDs).
   Drives `provenance_quality`.
2. **Confidence** — how certain we are the memory is correct. Influenced by
   source type, corroboration (multiple memories agree), and contradictions.
3. **Freshness** — recency relative to the memory's `type` (a `preference` ages
   differently than an `event`). Stale memories are down-weighted, not deleted.
4. **Explainability** — a human-readable explanation of why a memory was
   retrieved and how trust was computed.

## Result Shape (Phase 4)

```json
"trust": {
  "provenance_quality": 0.9,
  "confidence": 0.75,
  "freshness": 0.6,
  "explanation": "User-stated preference (high provenance), corroborated by 2
                  memories, last confirmed 12 days ago."
}
```

## How Trust Affects Retrieval

- Trust signals enter ranking fusion as weighted dimensions.
- Consumers can **filter** ("only confidence ≥ 0.7") or **weight** ("favor fresh").
- Trust never silently hides memories — effects are explained.

## Principles

- **No black boxes:** every trust score is decomposable into its inputs.
- **Auditable:** provenance and trust inputs are traceable to AuditEvents and
  source memories.
- **Calibrated, not absolute:** trust is a signal to weigh, not ground truth;
  calibration tracked in benchmarks.

## Risks (tracked)

- Mis-calibrated confidence → see [24-known-risks](24-known-risks.md).

## Phase Boundaries

- Depends on Phase 1 (provenance, audit), Phase 2 (importance/freshness inputs),
  Phase 3 (ranking to augment). Delivered in Phase 4.

## Related

[14-ranking-model](14-ranking-model.md) · [13-retrieval-model](13-retrieval-model.md) · [16-security-model](16-security-model.md) · [04-domain-model](04-domain-model.md)
