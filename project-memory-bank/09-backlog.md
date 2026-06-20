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
- [x] *Real embedding model behind `Embedder`* — offline sentence-transformers
  `all-MiniLM-L6-v2`, opt-in (`SCP_EMBEDDER=sentence-transformers`, ADR-011);
  delivered in Phase 5
- [ ] *Deferred to production hardening:* Qdrant in CI; FTS5/`tsvector` inverted
  index; weighted-vs-RRF benchmark on a fixed eval set

## Phase 4 — Trust Layer ✅ complete (2026-06-20)
- [x] Provenance quality scoring (source → quality)
- [x] Confidence (provenance floor + corroboration boost − contradiction penalty)
- [x] Freshness (type-aware half-lives)
- [x] Explainability output + explain endpoint (`GET /v1/trust/{memory_id}`)
- [x] Trust folded into ranking fusion; `min_confidence` filter on search
- [ ] *Deferred to production hardening:* semantic corroboration/contradiction
  (NLI) behind `trust_service`; trust calibration on a fixed eval set; multi-hop
  provenance-graph quality

## Phase 5 — SDK ✅ complete (2026-06-20)
- [x] Python SDK (`scp-memory-sdk`, httpx) — full surface incl. trust
- [x] TypeScript SDK (`@scp/memory-sdk`, Fetch) — full surface incl. trust
- [x] Offline local embedder behind `Embedder` (sentence-transformers, ADR-011)
- [ ] *Deferred:* publish to PyPI / npm; async Python client; generated API reference

## Phase 6 — Observability ✅ complete (2026-06-20)
- [x] Prometheus metrics + `/metrics` (counters + request-latency histogram)
- [x] OTel tracing wiring — opt-in (`SCP_TRACING_ENABLED`, `[observability]` extra),
  FastAPI + SQLAlchemy auto-instrumentation → OTLP → collector → Tempo (ADR-014)
- [x] Trace↔log correlation (`trace_id`/`span_id` in JSON logs); readiness probe
  (`/health/ready`) alongside liveness (`/health`)
- [x] SLOs as Prometheus recording + multi-window-burn alert rules; provisioned
  Grafana dashboard
- [x] Runnable stack (`deploy/observability/` docker-compose: app + collector +
  Tempo + Prometheus + Grafana) + `Dockerfile`
- [ ] *Deferred to production hardening:* manual per-stage retrieval spans
  (keyword/vector/ranking); Tempo on object storage; alert routing (PagerDuty)

## Phase 7 — Admin Console ✅ complete (2026-06-20)
- [x] Vite + React + TS SPA in `console/` (reuses `@scp/memory-sdk`); design tokens
  (Inter, 8-pt grid, light+dark) per [19-ui-design-system](19-ui-design-system.md) (ADR-015)
- [x] Dashboard (health + memory/retrieval/trust counters + API SLOs from `/metrics`)
- [x] Memory Explorer (filter/page/create/delete + per-memory fields & audit trail)
- [x] Retrieval Inspector (per-signal score bars + weights + trust; explainability)
- [x] Trust Explorer (provenance/confidence/freshness bars + explanation)
- [x] Benchmarks (live per-endpoint latency percentiles vs SLO targets)
- [x] Settings (namespace, engine base URL, actor, theme); required Empty/Loading/
  Error/keyboard/a11y states on every screen
- [x] Same-origin transport (Vite proxy in dev, reverse proxy in prod) — **no engine
  CORS change**; typecheck + 8 tests + production build green
- [ ] *Deferred to production hardening:* console auth/session; multi-origin hosting
  (opt-in CORS); historical trend charts (use Grafana/Tempo)

## Phase 8 — Android Reference App
- [ ] On-device semantic memory demo

## Cross-cutting / later
- [ ] Postgres backend in CI matrix
- [ ] Policy engine for lifecycle/governance
- [ ] pgvector evaluation vs Qdrant
- [ ] Neo4j evaluation for graph layer

## Related

[23-roadmap](23-roadmap.md) · [08-active-phase](08-active-phase.md) · [27-active-initiatives](27-active-initiatives.md)
