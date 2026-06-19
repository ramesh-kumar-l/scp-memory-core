# 09 — Backlog

**Status:** Active · **Last updated:** 2026-06-20

Ordered by phase. **No items are pulled into active work** until the relevant
phase is approved. The active phase is tracked in [08-active-phase](08-active-phase.md).

## Phase 1 — Memory Core (next, pending approval)
- [ ] Project skeleton: pyproject, package layout, tooling (ruff/black, pytest), CI
- [ ] SQLAlchemy models: `memories`, `provenance`, `audit_events`, `memory_relations`
- [ ] Memory service: create/read/update/delete with namespacing
- [ ] Audit trail: append-only event emission on every mutation
- [ ] FastAPI endpoints for CRUD + `/audit`
- [ ] Tests (unit + integration), metrics, logging, docs, examples, benchmark seed

## Phase 2 — Memory Intelligence
- [ ] Importance scoring (recency, frequency, explicit signals)
- [ ] Deduplication (semantic + metadata)
- [ ] Consolidation (summary memories with `derived_from`)
- [ ] Decay (importance over time → `decayed` state)

## Phase 3 — Hybrid Retrieval
- [ ] Keyword retrieval (FTS/BM25)
- [ ] Vector retrieval (Qdrant integration, embeddings)
- [ ] Metadata filtering
- [ ] Ranking engine (fusion: weighted vs RRF; benchmark to decide)

## Phase 4 — Trust Layer
- [ ] Provenance quality scoring
- [ ] Confidence (corroboration/contradiction)
- [ ] Freshness (type-aware)
- [ ] Explainability output + explain endpoint

## Phase 5 — SDK
- [ ] Python SDK
- [ ] TypeScript SDK

## Phase 6 — Observability
- [ ] Prometheus metrics + Grafana dashboards + OTel tracing wiring + SLOs

## Phase 7 — Admin Console
- [ ] Dashboard, Memory Explorer, Retrieval Inspector, Trust Explorer, Benchmarks, Settings

## Phase 8 — Android Reference App
- [ ] On-device semantic memory demo

## Cross-cutting / later
- [ ] Postgres backend in CI matrix
- [ ] Policy engine for lifecycle/governance
- [ ] pgvector evaluation vs Qdrant
- [ ] Neo4j evaluation for graph layer

## Related

[23-roadmap](23-roadmap.md) · [08-active-phase](08-active-phase.md) · [27-active-initiatives](27-active-initiatives.md)
