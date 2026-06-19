# 21 — Benchmark Results

**Status:** No results yet (Phase 0) · **Last updated:** 2026-06-20

Benchmarks are a quality gate and a public-build artifact. Each milestone updates
this file. No code exists yet, so there are no measurements.

## What We Measure

### Performance
- API latency p50/p95/p99 per endpoint
- CRUD throughput
- Retrieval latency by mode (keyword / vector / hybrid)
- Store latency (SQL, Qdrant)

### Quality (Phase 3+)
- Retrieval relevance: precision@k, recall@k, MRR, nDCG on a fixed eval set
- Dedup precision/recall (Phase 2)
- Trust calibration (Phase 4): predicted confidence vs. observed correctness

## Method (template)

- **Environment:** (CPU/RAM/OS, versions)
- **Dataset:** (size, source, eval set)
- **Procedure:** (warmup, runs, percentiles)
- **Config:** (k, mode, weights)

## Results

### Phase 0 — Foundation
n/a — no executable code. Baselines captured starting Phase 1.

| Milestone | Metric | Value | Notes |
|---|---|---|---|
| Phase 0 | — | — | No code yet |

## Related

[18-testing-strategy](18-testing-strategy.md) · [14-ranking-model](14-ranking-model.md) · [26-public-artifacts](26-public-artifacts.md)
