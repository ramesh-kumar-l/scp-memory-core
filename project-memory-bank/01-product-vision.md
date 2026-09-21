# 01 — Product Vision

**Status:** Active · **Phase:** 0 · **Last updated:** 2026-06-20

## Vision Statement

> **The Memory Infrastructure Layer for AI Systems.**

Just as databases became the default persistence layer for applications, SCP
Memory Engine aims to be the default *memory* layer for AI systems — a substrate
that any agent, assistant, or AI product can build on to remember, recall, and
reason over what it has learned, with trust and explainability built in.

## Product Pillars

1. **Persistent** — Memory survives sessions, processes, and devices. Durable
   storage with a clear lifecycle (create → consolidate → decay → forget).

2. **Explainable** — Every retrieval answers "why this memory?" Retrieval and
   ranking expose their signals; nothing is a black box.

3. **Trust-aware** — Memories carry provenance, confidence, and freshness.
   Consumers can weight or filter by trust, not just similarity.

4. **Governed** — Audit trail, access control, and lifecycle policies. Memory is
   inspectable, correctable, and deletable — enterprise- and privacy-ready.

5. **Portable** — Same model on-device and in the cloud. Local-first by default;
   scales out when needed.

## What "Good" Looks Like

- A developer adds memory to an agent in <10 minutes via SDK.
- They can open the Memory Explorer and see exactly what the agent remembers.
- They can ask "why did you retrieve this?" and get a real answer.
- They can set a policy ("forget low-importance memories older than 90 days").
- They can run the whole thing on a laptop, then deploy the same thing to cloud.

## Long-Term Direction

- Hybrid retrieval (keyword + vector + metadata + graph) as the standard.
- Trust scoring as a first-class retrieval dimension alongside relevance.
- Memory governance (policies, audit, GDPR-style deletion) as a default.
- An open ecosystem: open core, documented contracts, multi-language SDKs.

## Related

[00-project-charter](00-project-charter.md) · [02-product-thesis](02-product-thesis.md) · [15-trust-model](15-trust-model.md) · [23-roadmap](23-roadmap.md)
