# 25 — ADR Log

**Status:** Active · **Phase:** 5 · **Last updated:** 2026-06-20

Architecture Decision Records. Format: Context · Decision · Status · Consequences.
Phase 0 locks the recommended stack (ADR-001…010); Phase 5 adds ADR-011…012. All
**Accepted**. Narrative in [06-technical-decisions](06-technical-decisions.md).

---

## ADR-001 — Implementation language: Python 3.11+
- **Context:** Need fast iteration and a strong AI/ML ecosystem; SDK and server
  in one language family.
- **Decision:** Python 3.11+ for the engine and reference server.
- **Status:** Accepted (2026-06-20)
- **Consequences:** Excellent ecosystem and hiring; not the fastest runtime —
  mitigate hot paths via Qdrant and native libs. TypeScript SDK added in Phase 5.

## ADR-002 — API framework: FastAPI
- **Context:** Need a typed, async HTTP API with OpenAPI docs.
- **Decision:** FastAPI.
- **Status:** Accepted (2026-06-20)
- **Consequences:** Native Pydantic integration, auto OpenAPI; async-first.
  Couples us to Starlette/Pydantic conventions (acceptable).

## ADR-003 — Validation/models: Pydantic v2
- **Context:** Need strict, fast request/response and domain validation.
- **Decision:** Pydantic v2.
- **Status:** Accepted (2026-06-20)
- **Consequences:** Clear contracts and speed; v2 API differs from v1 (greenfield,
  so no migration cost).

## ADR-004 — ORM: SQLAlchemy 2.x
- **Context:** Need backend portability (SQLite↔Postgres) and maintainable data
  access.
- **Decision:** SQLAlchemy 2.x (with async where useful).
- **Status:** Accepted (2026-06-20)
- **Consequences:** Mature and portable; learning curve vs. lighter ORMs.

## ADR-005 — Database (MVP): SQLite
- **Context:** Local-first and on-device require zero-config storage.
- **Decision:** SQLite as the MVP relational store and source of truth.
- **Status:** Accepted (2026-06-20)
- **Consequences:** Trivial setup; concurrency/scale limits — addressed by ADR-006.

## ADR-006 — Database (scale): PostgreSQL
- **Context:** Cloud/scale deployments need concurrency and robustness.
- **Decision:** PostgreSQL as the scale backend, behind the same SQLAlchemy layer.
- **Status:** Accepted (2026-06-20)
- **Consequences:** Same domain model scales out; pgvector remains a future option
  that could simplify the vector tier.

## ADR-007 — Vector store: Qdrant
- **Context:** Need ANN search with strong metadata filtering, open source,
  local + cloud.
- **Decision:** Qdrant as the embedding/vector store.
- **Status:** Accepted (2026-06-20)
- **Consequences:** Good filtering and Python client; an extra service to run —
  acceptable; vector store is a derived, swappable index.

## ADR-008 — Graph layer: NetworkX (Neo4j optional later)
- **Context:** Need memory-to-memory relationships without heavy infra at MVP.
- **Decision:** NetworkX now; Neo4j optional later if needed.
- **Status:** Accepted (2026-06-20)
- **Consequences:** Zero infra, pure Python; in-memory scale limits — revisit at
  Phase 3+ if relationship queries become a bottleneck.

## ADR-009 — Observability: OpenTelemetry + Prometheus + Grafana
- **Context:** Need vendor-neutral, portable metrics/traces/logs.
- **Decision:** OpenTelemetry instrumentation → Prometheus metrics → Grafana
  dashboards.
- **Status:** Accepted (2026-06-20)
- **Consequences:** Standard and portable; instrumentation discipline required
  (a quality gate). Detail in [17-observability-model](17-observability-model.md).

## ADR-010 — Testing: Pytest (+ integration + benchmark)
- **Context:** Need a standard test framework supporting unit, integration, and
  benchmark layers.
- **Decision:** Pytest with integration and benchmark test suites.
- **Status:** Accepted (2026-06-20)
- **Consequences:** Rich ecosystem and fixtures; benchmark discipline required
  (a quality gate). Detail in [18-testing-strategy](18-testing-strategy.md).

## ADR-011 — Production embeddings: local sentence-transformers, opt-in (Phase 5)
- **Context:** Retrieval needs real *semantic* vectors, but the default/test path
  must stay hermetic and offline. The carried-over question: which model behind the
  `Embedder` seam, and must it run offline?
- **Decision:** `sentence-transformers` with `all-MiniLM-L6-v2` (384-dim) — runs
  **fully on-device, no embedding API**. Selected via `SCP_EMBEDDER=sentence-`
  `transformers` (needs the `[embeddings]` extra); `embedding_offline=True` pins the
  loader to the local HF cache (air-gap safe). The deterministic `HashingEmbedder`
  stays the offline-by-default stand-in so CI needs no model.
- **Status:** Accepted (2026-06-20)
- **Consequences:** Real semantics on demand without changing retrieval/ranking/
  vector code; opt-in keeps tests fast and network-free. Explicit selection fails
  loudly if the model can't load (no silent degradation). Qdrant collections must
  match the model's dimension when used together. NLI for trust remains deferred.

## ADR-012 — SDK stack: httpx (Python) + Fetch API (TypeScript) (Phase 5)
- **Context:** Phase 5 needs official clients over the full, stable API including
  trust, integration-test-friendly and runnable in many environments.
- **Decision:** Python SDK wraps `httpx` (sync) with an injectable client; the
  TypeScript SDK uses the global `fetch` (Node 18+/browser/Deno) with an injectable
  `fetchFn`. Both are thin, typed, 1:1 with the API schemas, with a typed error
  hierarchy and forward-compatible parsing.
- **Status:** Accepted (2026-06-20)
- **Consequences:** Tests run in-process (FastAPI `TestClient` / stubbed fetch) with
  no server; minimal dependencies. Sync-only Python (async deferred); SDKs version
  independently (0.5.0) tracking the engine. Detail in
  [../docs/phase-5-sdks.md](../docs/phase-5-sdks.md).

---

## Process

- New significant decisions get the next ADR number here and a note in
  [06-technical-decisions](06-technical-decisions.md).
- Superseding decisions reference the ADR they replace; never edit a decided ADR's
  history — add a new one with status `Supersedes ADR-xxx`.

## Related

[06-technical-decisions](06-technical-decisions.md) · [03-system-architecture](03-system-architecture.md)
