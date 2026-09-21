# 00 — Project Charter

**Status:** Active · **Phase:** 0 (Foundation) · **Last updated:** 2026-06-20

## Project

**SCP Memory Engine** (`scp-memory-core`) — the Memory Infrastructure Layer for AI Systems.

## Mission

Provide production-grade, trustworthy, explainable, and extensible memory
infrastructure for AI systems: persistent memory, consolidation, lifecycle
management, context retrieval, and trust-aware, explainable recall — deployable
on-device and in the cloud, open source.

## Problem

AI systems today bolt memory on as ad-hoc vector search over chat logs. The
result is unreliable: no provenance, no notion of trust or freshness, no
lifecycle (memories never decay, duplicate endlessly), opaque retrieval ("why
was this returned?"), and no governance. Teams rebuild the same fragile layer
repeatedly. There is no shared, inspectable, trustworthy memory substrate.

## Target Users

- AI Engineers building memory into products
- Agent builders needing durable, queryable agent memory
- Enterprise AI teams needing governance, audit, and explainability
- Android/OEM teams needing on-device semantic memory
- Personal AI builders wanting a local-first memory store

## Success Criteria

Engineers can:
- Install it in minutes
- Understand it quickly
- **Trust** the results (provenance, confidence, freshness)
- **Explain** the results (why a memory was retrieved/ranked)
- Extend the system (clear contracts, SDKs)
- Run locally or in cloud (and on-device)

The product becomes the default memory infrastructure layer for AI systems.

## In Scope

- Memory entity model + storage + CRUD + audit (Phase 1)
- Importance, dedup, consolidation, decay (Phase 2)
- Hybrid retrieval + ranking (Phase 3)
- Trust layer: provenance, confidence, freshness, explainability (Phase 4)
- Python + TypeScript SDKs (Phase 5)
- Observability (Phase 6), Admin console (Phase 7), Android reference app (Phase 8)

## Out of Scope (for now)

- Training/fine-tuning models
- Being a general-purpose vector database
- Hosting/managing customer LLMs
- Proprietary closed-source features

## Operating Constraints

- Never rewrite working code; build incrementally on existing implementation.
- One active phase at a time; stop and await approval at each phase boundary.
- Every feature passes the quality gates (see [05-engineering-principles](05-engineering-principles.md)).
- Memory bank is the source of truth; read before every task.

## Related

[01-product-vision](01-product-vision.md) · [02-product-thesis](02-product-thesis.md) · [03-system-architecture](03-system-architecture.md) · [23-roadmap](23-roadmap.md)
