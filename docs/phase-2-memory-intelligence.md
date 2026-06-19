# Phase 2 — Memory Intelligence

Memory that manages itself: it scores its own importance, removes duplicates,
consolidates related items into summaries, and ages out stale knowledge. Builds
directly on [Phase 1 — Memory Core](phase-1-memory-core.md); design intent is in
[12-memory-model](../project-memory-bank/12-memory-model.md).

## What's implemented

- **Importance scoring** (`intelligence/scoring.py`, `services/importance_service.py`):
  a value in `[0, 1]` fusing **recency** (exponential decay, configurable
  half-life), **frequency** (saturating function of `access_count`), and an
  **explicit** metadata signal (`pinned` / `importance_hint`). Set at create,
  refreshed on every access, recomputed during decay.
- **Deduplication** (`services/dedup_service.py`): clusters active memories of the
  same type by lexical similarity (`intelligence/similarity.py`, token-set
  Jaccard), keeps one canonical memory, archives the rest, and records a
  `supersedes` edge from canonical → duplicate.
- **Consolidation** (`services/consolidation_service.py`): merges ≥2 active
  sources into a new `summary` memory, records `derived_from` edges and source IDs
  in provenance, and transitions the sources to `consolidated`.
- **Decay** (`services/decay_service.py`): recomputes importance across a
  namespace and transitions memories below the threshold to `decayed`.
- **Graph edges** (`services/relation_service.py`): first write paths into
  `memory_relations` (`derived_from`, `supersedes`).

Every transition emits an audit event in the same transaction as the change, and
provenance is never lost — the Phase 1 invariants still hold.

## Lexical, not semantic (yet)

Phase 2 similarity is **lexical** (Jaccard over tokens). Embedding-based semantic
similarity arrives with the vector store in **Phase 3**; the dedup service is
structured so the scorer can be swapped without touching the merge logic.

## API

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/intelligence/decay` | Age out low-importance memories in a namespace |
| POST | `/v1/intelligence/dedup` | Merge near-duplicate memories |
| POST | `/v1/intelligence/consolidate` | Build a summary from source memories (→ 201) |

- Each batch endpoint takes `{"namespace": "...", "threshold": <optional override>}`.
- `consolidate` takes `{"namespace", "source_ids": [≥2], "summary": <optional>}`;
  invalid/cross-namespace/non-active sources return **400**.
- `importance` and `access_count` now appear on every `MemoryRead`.
- **Default listing changed:** `GET /v1/memories` without a `state` filter now
  returns only `active` memories. Lifecycle by-products
  (`consolidated`/`decayed`/`archived`/`deleted`) are reachable by passing `state`
  explicitly. This keeps merged duplicates and summaries out of the default set.

## Configuration

Environment-driven (`SCP_` prefix):

| Setting | Default | Meaning |
|---|---|---|
| `SCP_DECAY_THRESHOLD` | `0.25` | importance below this → `decayed` |
| `SCP_DEDUP_SIMILARITY_THRESHOLD` | `0.85` | Jaccard at/above this → duplicate |

Scoring weights/half-life live in `ScoringConfig` (`intelligence/scoring.py`).

## Run it

```bash
pip install -e ".[dev]"
python examples/intelligence_quickstart.py   # importance → dedup → consolidate → decay
```

## Scalability notes

- Dedup is an O(n²) pairwise scan **within each (namespace, type) group** — fine
  for batch maintenance at MVP scale. Phase 3's vector index enables ANN candidate
  generation to replace the quadratic pass.
- Importance is maintained incrementally on the hot path (create/access); the
  batch decay pass handles purely time-based recompute.

## Tests

```bash
pytest -m "not benchmark"   # 46 unit + integration tests
```

Pure scoring/similarity functions are unit-tested in isolation; each service has
its own behavioural tests; the API is covered end-to-end in
`tests/integration/test_intelligence_api.py`.

## Not in Phase 2 (by design)

Retrieval and ranking (Phase 3) — importance is computed here but consumed by the
ranking engine later. LLM-generated summaries are a later enhancement; the merge
graph and provenance are identical regardless of how summary text is produced.
