# Phase 3 — Hybrid Retrieval

Finding the right memories. Retrieval is **hybrid**: a metadata filter scopes the
search, lexical (keyword) and semantic (vector) generators produce candidates, and
a ranking engine **fuses** their scores together with Phase-2 `importance` into a
single, **explainable** ordering. Design intent:
[13-retrieval-model](../project-memory-bank/13-retrieval-model.md) and
[14-ranking-model](../project-memory-bank/14-ranking-model.md).

## What's implemented

- **Embeddings** (`retrieval/embedding.py`): a deterministic, dependency-free
  `HashingEmbedder` (feature-hashing → L2-normalized vector) behind an `Embedder`
  protocol, plus `cosine_similarity`. Pure, hermetic, reproducible.
- **Keyword scoring** (`retrieval/keyword.py`): pure Okapi **BM25** over the
  metadata-filtered candidate corpus.
- **Fusion** (`retrieval/fusion.py`): `weighted_fuse` (min-max normalize each
  relevance signal, then a weighted linear combination — the default, fully
  explainable) and `reciprocal_rank_fusion` (rank-based, scale-robust).
- **Vector backends** (`services/vector_backend.py`): a `VectorBackend` protocol
  with an in-process `BruteForceBackend` (default) and a lazily-loaded Qdrant
  adapter (`services/qdrant_backend.py`) for scale.
- **Orchestration** (`services/retrieval_service.py`): metadata filter (SQL) →
  keyword ∪ vector candidates → fuse → rank → top-k explainable results. Retrieval
  **touches** the returned hits (`last_accessed_at`, `access_count`, recomputed
  `importance`), feeding the Phase-2 importance/decay loop.

## Explainability contract

Every result carries the per-signal scores and the weights that produced its rank:

```json
{ "memory": { ... },
  "score": 0.90,
  "signals": { "keyword": 1.0, "vector": 1.0, "metadata": 1.0, "importance": 0.5 },
  "weights": { "keyword": 0.4, "vector": 0.4, "importance": 0.2 } }
```

`keyword` and `vector` are **normalized across the result set** (so the numbers
explain *relative* rank within this query); `importance` is the absolute Phase-2
value; `metadata` is `1.0` for candidates that satisfied the filter constraints.

## Honest scope: the embedder is a deterministic stand-in

The default `HashingEmbedder` produces semantic-*shaped* vectors, but similarity is
driven by **shared tokens and hash buckets — not true meaning**. It exists so the
whole pipeline runs with zero external infra and deterministic tests. The
`Embedder` protocol is the seam where a real model (sentence-transformers, a hosted
embedding API) drops in for production-grade semantics **without touching**
retrieval, ranking, or the backend. This mirrors Phase 2's "lexical now" honesty.

## Vector backend: default vs. scale path

| Backend | When | Notes |
|---|---|---|
| `bruteforce` (default) | always available | Embeds candidates live, cosine in-process. O(N)/query. Zero infra; the **tested** path. |
| `qdrant` | `SCP_VECTOR_BACKEND=qdrant` | Native ANN over persisted vectors. Needs the `[vector]` extra + a running Qdrant. **Integration-only — not exercised by CI.** |

The relational store stays the source of truth; the Qdrant collection is derived
and rebuildable via `QdrantBackend.reindex(...)`.

## API

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/retrieval/search` | Hybrid (or keyword/vector) retrieval with ranking |

Request: `{"query", "namespace", "k"≤100, "mode": keyword|vector|hybrid, "type"?, "state"?}`
(defaults: `mode=hybrid`, `k=10`, `state=active`). Blank query/namespace → **422**.

## Configuration

| Setting | Default | Meaning |
|---|---|---|
| `SCP_VECTOR_BACKEND` | `bruteforce` | `bruteforce` or `qdrant` |
| `SCP_QDRANT_URL` | `http://localhost:6333` | Qdrant endpoint (qdrant backend) |
| `SCP_QDRANT_COLLECTION` | `scp_memories` | Qdrant collection name |

Algorithmic knobs (embedding dim, `k` bounds, candidate cap, fusion weights) live
in `RetrievalConfig` / `FusionWeights` (`retrieval/config.py`, `retrieval/fusion.py`).

## Run it

```bash
pip install -e ".[dev]"
python examples/retrieval_quickstart.py     # hybrid + keyword-only search
```

## Scalability notes

- Default keyword + brute-force vector are each **O(N) per query within a
  namespace**, bounded by `candidate_limit` (latency guard). Fine at MVP scale.
- The production scale path is: a real embedding model + the Qdrant ANN backend for
  vectors, and an inverted index (SQLite FTS5 / Postgres `tsvector`) for keyword.
  Both slot in behind the existing seams without changing the ranking pipeline.

## Tests

```bash
pytest -m "not benchmark"   # 70 unit + integration tests
```

Pure embedding/BM25/fusion functions are unit-tested in isolation;
`tests/unit/test_retrieval_service.py` covers orchestration (ranking, namespace
isolation, touch, filters); `tests/integration/test_retrieval_api.py` covers the
endpoint end-to-end.

## Not in Phase 3 (by design)

Trust signals — provenance quality, confidence, freshness — are layered onto these
results in **Phase 4**; the ranking fusion already has the slot for them. A real
embedding model and the Qdrant integration env are production-hardening steps, not
new logic.
