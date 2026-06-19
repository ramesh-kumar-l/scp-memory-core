# 02 — Product Thesis

**Status:** Active · **Phase:** 0 · **Last updated:** 2026-06-20

## Thesis

AI systems are moving from stateless prompt-response to long-lived agents.
Long-lived agents need *memory* — not just a vector index, but a managed,
trustworthy, explainable memory layer. That layer does not exist as shared
infrastructure today. SCP Memory Engine builds it.

## Why Now

- Agents and assistants are becoming persistent and multi-session.
- Context windows are large but expensive and lossy; you can't put everything
  in-context forever. Selective, ranked, trustworthy recall is required.
- Enterprises adopting AI demand governance, audit, and explainability — exactly
  what naive RAG-over-logs lacks.
- On-device AI (phones, OEM assistants) needs a local-first memory layer.

## The Gap in Current Approaches

| Current approach | Limitation |
|---|---|
| Vector DB over chat logs | No provenance, trust, or freshness; opaque ranking |
| RAG frameworks | Retrieval-as-plumbing; no memory lifecycle or governance |
| Agent memory libraries | Tied to one framework; no audit, weak explainability |
| Long context windows | Costly, lossy, no persistence across sessions/devices |

The common failure: **memory is treated as similarity search, not as managed,
accountable infrastructure.**

## Differentiation

SCP competes on **trust + explainability + governance + portability**, not on
being the fastest vector store:

- **Trust-aware retrieval** — provenance, confidence, freshness as first-class.
- **Explainable recall** — every result carries the signals that produced it.
- **Memory lifecycle** — importance, dedup, consolidation, decay, deletion.
- **Governance** — audit trail and policies by default.
- **Portability** — same engine local, cloud, and on-device.
- **Open core** — inspectable, extensible, community-driven.

## Bet

If memory becomes the durable, trustworthy substrate for AI — the way databases
did for apps — then the team that ships the most *trustworthy and explainable*
memory layer, open and portable, wins the category.

## Related

[01-product-vision](01-product-vision.md) · [22-competitive-analysis](22-competitive-analysis.md) · [15-trust-model](15-trust-model.md)
