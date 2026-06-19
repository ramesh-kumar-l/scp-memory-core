# 22 — Competitive Analysis

**Status:** Active · **Phase:** 0 · **Last updated:** 2026-06-20

## Landscape

| Category | Examples | Strength | Gap SCP fills |
|---|---|---|---|
| Vector databases | Qdrant, Pinecone, Weaviate, Milvus, pgvector | Fast ANN search at scale | No memory lifecycle, trust, provenance, or explainability — they are *storage*, not *memory* |
| Agent memory libs | LangChain/LangGraph memory, LlamaIndex, Letta/MemGPT, Zep, Mem0 | Convenient agent integration | Framework-coupled; weak governance/audit; limited explainability and trust scoring |
| RAG frameworks | LlamaIndex, Haystack, DSPy | Retrieval pipelines | Retrieval-as-plumbing; no managed memory lifecycle or trust layer |
| Long context / KV | Large-context LLMs, KV caches | Simple, no infra | Costly, lossy, non-persistent across sessions/devices |
| Knowledge graphs | Neo4j, graph RAG | Structured relations | High setup cost; not a turnkey memory layer; weak on freshness/decay |

## Where SCP Differs

SCP is **not** trying to be the fastest vector DB. It sits *above* the vector
store and *around* the agent, providing:

1. **Trust-aware retrieval** — provenance, confidence, freshness as ranking
   dimensions, not just cosine similarity.
2. **Explainable recall** — every result exposes the signals that produced it.
3. **Memory lifecycle** — importance scoring, deduplication, consolidation,
   decay, and governed deletion.
4. **Governance** — audit trail and lifecycle policies by default.
5. **Portability** — same engine local, cloud, and on-device.
6. **Open core** — documented contracts, multi-language SDKs.

We *use* a vector DB (Qdrant) rather than compete with it.

## Positioning Statement

> For AI engineers building long-lived agents, SCP Memory Engine is the open
> memory infrastructure layer that makes recall persistent, trustworthy, and
> explainable — unlike vector DBs (storage only) or agent memory libs
> (framework-locked, no governance).

## Watch List (revisit each milestone)

- Mem0, Zep, Letta/MemGPT — closest "AI memory" positioning.
- pgvector + Postgres — viable lightweight competitor for the storage tier.
- Native memory features shipped by LLM providers.

## Related

[02-product-thesis](02-product-thesis.md) · [01-product-vision](01-product-vision.md) · [13-retrieval-model](13-retrieval-model.md)
