# 03 — System Architecture

**Status:** Active · **Phase:** 0 (design intent) · **Last updated:** 2026-06-20

This is the target architecture. Components are introduced phase by phase (see
[23-roadmap](23-roadmap.md)); not all exist yet. No code exists as of Phase 0.

## High-Level Component View

```
                         ┌───────────────────────────────────────┐
                         │              Clients                   │
                         │  Agents · Apps · SDKs (Py/TS) · Console│
                         └───────────────────┬───────────────────┘
                                             │ HTTP / SDK
                         ┌───────────────────▼───────────────────┐
                         │              API Layer                 │
                         │           FastAPI + Pydantic           │
                         │   CRUD · Retrieve · Trust · Admin      │
                         └───┬───────────┬───────────┬───────────┘
                             │           │           │
              ┌──────────────▼──┐ ┌──────▼───────┐ ┌─▼───────────────┐
              │  Memory Service │ │  Retrieval   │ │  Trust Service  │
              │  CRUD, lifecycle│ │  Engine      │ │  provenance,    │
              │  importance,    │ │  keyword +   │ │  confidence,    │
              │  dedup, decay,  │ │  vector +    │ │  freshness,     │
              │  consolidation  │ │  metadata +  │ │  explainability │
              │                 │ │  ranking     │ │                 │
              └───┬─────────┬───┘ └──┬────────┬──┘ └────────┬────────┘
                  │         │        │        │             │
        ┌─────────▼──┐ ┌────▼─────┐ ┌▼────────▼─┐ ┌─────────▼────────┐
        │ Relational │ │  Audit   │ │  Vector   │ │   Graph Layer    │
        │  Store     │ │  Trail   │ │  Store    │ │   (NetworkX)     │
        │ SQLite →   │ │ (events) │ │ (Qdrant)  │ │  relations       │
        │ Postgres   │ │          │ │ embeddings│ │                  │
        └────────────┘ └──────────┘ └───────────┘ └──────────────────┘

   Cross-cutting: Observability (OpenTelemetry → Prometheus/Grafana),
                  Security & Governance (authz, policies, audit).
```

## Components

- **API Layer (FastAPI + Pydantic):** typed HTTP surface. Endpoints for memory
  CRUD, retrieval, trust, and admin. See [10-api-contracts](10-api-contracts.md).
- **Memory Service:** owns the memory entity lifecycle — create/read/update/
  delete, importance scoring, deduplication, consolidation, decay. See
  [12-memory-model](12-memory-model.md).
- **Retrieval Engine:** hybrid retrieval (keyword + vector + metadata) feeding a
  ranking/fusion stage. See [13-retrieval-model](13-retrieval-model.md),
  [14-ranking-model](14-ranking-model.md).
- **Trust Service:** attaches provenance, confidence, freshness, and
  explanations to results. See [15-trust-model](15-trust-model.md).
- **Relational Store (SQLite → PostgreSQL):** source of truth for memory records
  and metadata, via SQLAlchemy. See [11-data-models](11-data-models.md).
- **Vector Store (Qdrant):** embeddings + ANN search for semantic retrieval.
- **Graph Layer (NetworkX):** relationships between memories; optional Neo4j later.
- **Audit Trail:** append-only event log of all memory mutations. See
  [16-security-model](16-security-model.md).
- **Observability:** OpenTelemetry traces/metrics → Prometheus/Grafana. See
  [17-observability-model](17-observability-model.md).

## Deployment Modes

- **Local / on-device:** single process, SQLite, embedded/local vector index.
  Local-first by default.
- **Cloud / scale:** PostgreSQL, Qdrant cluster, horizontal API scaling.
- **Android reference (Phase 8):** on-device semantic memory using the same
  domain model.

## Design Tenets

- Storage is pluggable; the domain model is stable. The relational store is the
  source of truth; the vector store is a derived index.
- Retrieval results are always explainable: signals travel with results.
- Same domain model across deployment modes.

## Related

[04-domain-model](04-domain-model.md) · [06-technical-decisions](06-technical-decisions.md) · [25-adr-log](25-adr-log.md) · [16-security-model](16-security-model.md)
