# 18 — Testing Strategy

**Status:** Active policy · **Last updated:** 2026-06-20

Tests are a quality gate: no feature is complete without them
([05-engineering-principles](05-engineering-principles.md)). Framework: **Pytest**
with integration and benchmark layers ([ADR-010](25-adr-log.md)).

## Test Layers

### Unit tests
- Pure logic: importance scoring, dedup detection, decay math, ranking fusion,
  trust computation.
- Fast, no external services; in-memory or SQLite-temp.

### Integration tests
- API ↔ service ↔ stores end-to-end.
- Real SQLite (and Postgres in CI matrix later); real/embedded Qdrant for
  retrieval paths.
- Cover CRUD + audit, retrieval pipeline, trust attachment.

### Benchmark tests
- Latency and quality (e.g., retrieval relevance metrics) tracked over time.
- Results recorded in [21-benchmark-results](21-benchmark-results.md); each
  milestone updates them (public-build requirement).

## What Every Feature Must Test

- Happy path + key error cases (no tests for impossible cases — keep it lean).
- Audit emission on mutations.
- Explainability: retrieval/ranking results expose expected signals.
- Invariants from [12-memory-model](12-memory-model.md) (state transitions,
  provenance preservation).

## Conventions

- `tests/unit`, `tests/integration`, `tests/benchmark` (created in Phase 1).
- Deterministic tests; seed randomness; isolate temp DBs per test.
- CI runs unit + integration on every change; benchmarks on milestones.

## Goal-Driven Testing

Per the working agreement, transform tasks into verifiable goals: write the test
that encodes the requirement (or reproduces the bug), then make it pass.

## Related

[05-engineering-principles](05-engineering-principles.md) · [21-benchmark-results](21-benchmark-results.md) · [17-observability-model](17-observability-model.md)
