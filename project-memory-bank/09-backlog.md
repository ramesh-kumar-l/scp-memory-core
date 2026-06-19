# 09 — Backlog

**Status:** Active · **Last updated:** 2026-06-20

Ordered by phase. **No items are pulled into active work** until the relevant
phase is approved. The active phase is tracked in [08-active-phase](08-active-phase.md).

## Phase 1 — Memory Core ✅ complete (2026-06-20)
- [x] Project skeleton: pyproject, package layout, tooling (ruff/black, pytest), CI
- [x] SQLAlchemy models: `memories`, `provenance`, `audit_events`, `memory_relations`
- [x] Memory service: create/read/update/delete with namespacing
- [x] Audit trail: append-only event emission on every mutation
- [x] FastAPI endpoints for CRUD + `/audit`
- [x] Tests (unit + integration), metrics, logging, docs, examples, benchmark seed

## Phase 2 — Memory Intelligence ✅ complete (2026-06-20)
- [x] Importance scoring (recency, frequency, explicit signals)
- [x] Deduplication (lexical Jaccard + per-type/namespace; semantic = Phase 3)
- [x] Consolidation (summary memories with `derived_from`)
- [x] Decay (importance over time → `decayed` state)

## Phase 3 — Hybrid Retrieval ✅ complete (2026-06-20)
- [x] Keyword retrieval (pure Okapi BM25 over filtered candidates)
- [x] Vector retrieval (`HashingEmbedder` stand-in + cosine; Qdrant backend seam)
- [x] Metadata filtering (namespace/type/state constraints)
- [x] Ranking engine (weighted-linear default + RRF; importance as a signal)
- [ ] *Deferred to production hardening:* real embedding model behind `Embedder`;
  Qdrant in CI; FTS5/`tsvector` inverted index; weighted-vs-RRF benchmark on a
  fixed eval set

## Phase 4 — Trust Layer ✅ complete (2026-06-20)
- [x] Provenance quality scoring (source → quality)
- [x] Confidence (provenance floor + corroboration boost − contradiction penalty)
- [x] Freshness (type-aware half-lives)
- [x] Explainability output + explain endpoint (`GET /v1/trust/{memory_id}`)
- [x] Trust folded into ranking fusion; `min_confidence` filter on search
- [ ] *Deferred to production hardening:* semantic corroboration/contradiction
  (NLI) behind `trust_service`; trust calibration on a fixed eval set; multi-hop
  provenance-graph quality

## Phase 5 — SDK (next, pending approval)
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
