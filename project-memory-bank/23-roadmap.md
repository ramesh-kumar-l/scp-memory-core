# 23 — Roadmap

**Status:** Active · **Phase:** 4 complete · **Last updated:** 2026-06-20

Phases are executed strictly in order. Only one phase is active at a time; work
stops at each boundary for explicit approval. See [08-active-phase](08-active-phase.md)
for the current phase.

| Phase | Name | Outcome | Key deliverables |
|---|---|---|---|
| **0** | Project Foundation | Shared source of truth + locked decisions | Vision, ADRs, architecture, **memory bank** |
| **1** | Memory Core | Durable, auditable CRUD over memories | Memory entity model, storage layer, CRUD APIs, audit trail |
| **2** | Memory Intelligence | Memory manages itself | Importance scoring, deduplication, consolidation, decay |
| **3** | Hybrid Retrieval | Relevant recall across signals | Keyword + vector + metadata retrieval, ranking engine |
| **4** | Trust Layer | Trustworthy & explainable recall | Provenance, confidence, freshness, explainability |
| **5** | SDK | Easy integration | Python SDK, TypeScript SDK |
| **6** | Observability | Operable in production | Metrics, logging, tracing |
| **7** | Admin Console | Inspectable memory | Memory Explorer, Retrieval Explorer, Trust Explorer |
| **8** | Android Reference App | On-device proof | On-device semantic memory demo |

## Sequencing Rationale

- **Core before intelligence:** you cannot consolidate/decay what you cannot
  durably store and audit.
- **Intelligence before retrieval:** importance and dedup shape what retrieval
  ranks over.
- **Retrieval before trust:** the trust layer augments retrieval results; it
  needs a working ranking pipeline to attach signals to.
- **SDK after trust:** SDKs should expose the full, stable surface including
  trust signals.
- **Observability + console before on-device:** operability and inspection make
  the reference app credible.

## Current Position

Phases 0–4 complete. Memory Core (audited, namespaced CRUD), Memory Intelligence
(importance, dedup, consolidation, decay), Hybrid Retrieval (keyword + vector +
metadata + explainable ranking), and the Trust Layer (provenance, confidence,
freshness, explainability — folded into ranking) are shipped and tested (86
tests). Next: Phase 5 (SDK), to begin **only after explicit approval**.

## Related

[08-active-phase](08-active-phase.md) · [09-backlog](09-backlog.md) · [20-release-plan](20-release-plan.md)
