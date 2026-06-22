# Quick Starter Guide

> Zero-to-running for a newbie engineer who just cloned `scp-memory-core`. If you've never
> seen this project before, read top to bottom — every question you're about to have is
> answered here.

---

## 1. What is this, in one paragraph?

**SCP Memory Engine** is a *memory layer for AI agents*. Where a vector database just stores
embeddings and returns the nearest match, this engine stores **memories** and, on every
retrieval, tells you **why** a memory surfaced (per-signal scores) and **how much to trust
it** (a decomposable trust score from provenance, corroboration, and freshness) — with an
append-only audit trail underneath. Think: *a database that has judgment about what it
remembers.* The "why this matters" essay is
[`documents/04-engineering-thesis.md`](documents/04-engineering-thesis.md).

## 2. What's in the box? (repo map)

| Path | What it is |
|---|---|
| `src/scp_memory/` | The engine: FastAPI app, models, retrieval, trust, services, observability |
| `examples/` | Runnable scripts that exercise the API end-to-end |
| `seed/` | Loads the **10 Golden Examples** into the engine ([`seed/README.md`](seed/README.md)) |
| `documents/` | Strategy + architecture + ADRs + benchmark + the 10-example dataset |
| `blog_series/` | Publish-ready deep-dive articles (with diagrams) |
| `sdks/python`, `sdks/typescript` | Official client SDKs |
| `console/` | Admin Console — a web UI over every signal (React + Vite) |
| `deploy/observability/` | Docker Compose stack: app + Prometheus + Grafana + Tempo |
| `evals/` | Offline benchmark + trust-calibration harnesses |
| `project-memory-bank/` | The project's "brain" — 29 numbered docs; the source of truth |
| `tests/` | Pytest suite (132 passing) |

## 3. Prerequisites

- **Python 3.11+** (required). Check: `python --version`.
- **git**. That's it for the default path — **no GPU, no Docker, no external database
  needed.** The engine runs hermetically on SQLite out of the box.
- Optional later: Node 18+ (for the TypeScript SDK / console), Docker (for the
  observability stack), Android Studio (for the reference app).

## 4. Install & run (the 60-second path)

```bash
git clone <repo-url> && cd scp-memory-core
python -m venv .venv && . .venv/Scripts/activate   # Windows; use .venv/bin/activate on macOS/Linux
pip install -e ".[dev]"                             # engine + test/HTTP deps
```

Run the engine:

```bash
python -m scp_memory          # serves http://localhost:8000
```

Check it's alive (in another terminal):

```bash
curl http://localhost:8000/health          # {"status":"ok"}
```

Open the interactive API docs at **http://localhost:8000/docs**.

## 5. See it actually do something — the 10 Golden Examples

The fastest way to *understand* the engine is to load 10 curated memories and query them.

```bash
# with the engine running (step 4):
python seed/seed_golden_examples.py

# …or with no server at all (in-process, uses the engine's SQLite file):
python seed/seed_golden_examples.py --in-process
```

You'll see 10 memories created and a trust-scored sample search. Each example is chosen to
show one capability — a contradiction (dark vs light mode), a consolidation summary, an
inferred vs. user-stated memory, event decay, metadata-rich finance retrieval, a gallery
photo. Full table + demo queries:
[`documents/11-demo-and-examples-pack.md`](documents/11-demo-and-examples-pack.md).

Verify them:

```bash
curl 'http://localhost:8000/v1/memories?namespace=demo:golden'    # expect 10 items
python seed/seed_golden_examples.py --reset                       # clean up
```

## 6. The other runnable examples

```bash
python examples/quickstart.py              # CRUD + audit trail, in-process
python examples/retrieval_quickstart.py    # hybrid retrieval with per-signal scores
python examples/trust_quickstart.py        # a trust breakdown + explanation
python examples/intelligence_quickstart.py # dedup / consolidate / decay passes
python examples/sdk_quickstart.py          # using the Python SDK
```

## 7. The five concepts you need

1. **Memory** — a stored item with a `type` (`fact` / `event` / `preference` / `summary`),
   `content`, `metadata`, and `provenance`. Scoped by a **namespace** (the tenant/owner).
2. **Provenance** — *who said it*: `user` (1.0) → `consolidation` (0.75) → `inferred` (0.5)
   → `system` (0.4). Drives the trust floor.
3. **Trust** — a decomposable score = **provenance × confidence × freshness**, with a
   human-readable explanation. Confidence rises with corroboration, falls with
   contradiction; freshness decays faster for `event` (~14d half-life) than `preference`
   (~180d).
4. **Hybrid retrieval** — keyword (BM25) ∪ vector ∪ metadata, fused and ranked, with trust
   as a ranking dimension. Every result carries its per-signal scores.
5. **Lifecycle / intelligence** — importance scoring, deduplication, **consolidation**
   (summaries with `derived_from`), and **decay**. Memory isn't write-once.

Deeper: [`documents/05-architecture-document.md`](documents/05-architecture-document.md) and
[`project-memory-bank/15-trust-model.md`](project-memory-bank/15-trust-model.md).

## 8. API cheat sheet

```bash
# create
curl -X POST localhost:8000/v1/memories -H 'Content-Type: application/json' \
  -H 'X-Actor: me' \
  -d '{"content":"User prefers dark mode","namespace":"user:1","type":"preference","source":"user"}'

# list
curl 'localhost:8000/v1/memories?namespace=user:1'

# retrieve (explainable + trust-scored)
curl -X POST localhost:8000/v1/retrieval/search -H 'Content-Type: application/json' \
  -d '{"query":"what theme?","namespace":"user:1","k":5}'

# trust breakdown for one memory
curl localhost:8000/v1/trust/<memory_id>

# audit trail
curl localhost:8000/v1/memories/<memory_id>/audit
```

Full contract: [`project-memory-bank/29-api-contracts.md`](project-memory-bank/29-api-contracts.md).

## 9. The Admin Console (see the signals visually)

```bash
cd console
npm install
npm run dev            # opens a UI that proxies to the engine on :8000
```

Memory Explorer, Retrieval Inspector (per-signal score bars), Trust Explorer, Benchmarks.
After seeding the golden examples, set the namespace to `demo:golden` to view them.

## 10. Run the tests & quality gates

```bash
pytest                 # 132 tests, hermetic (no network)
ruff check src tests   # lint
black --check src tests # format
python evals/run_retrieval_benchmark.py   # nDCG/MRR, weighted vs RRF
python evals/run_trust_calibration.py     # Brier / ECE
```

## 11. Going beyond the defaults (opt-in scale paths)

The defaults are hermetic stand-ins. Real quality and scale are opt-in via env vars + extras
— **the API contract never changes**:

| Want | Install / set |
|---|---|
| Real semantic embeddings | `pip install -e ".[embeddings]"` + `SCP_EMBEDDER=sentence-transformers` |
| Vector ANN at scale | `pip install -e ".[vector]"` + `SCP_VECTOR_BACKEND=qdrant` |
| Inverted-index keyword search | `SCP_KEYWORD_BACKEND=fts5` (SQLite) / `tsvector` (Postgres) |
| NLI-based trust detection | `SCP_TRUST_NLI=1` (gated on a calibration win — see ADR-06) |
| Tracing | `pip install -e ".[observability]"` + `SCP_TRACING_ENABLED=true` |

Config prefix is `SCP_`. **Never commit secrets** — pass tokens as environment variables.

## 12. Troubleshooting / FAQ

- **`ModuleNotFoundError: scp_memory`** → run `pip install -e ".[dev]"` inside your venv.
- **`--in-process` seeder fails on import** → it needs `httpx` (included in the `dev`
  extra). Install `.[dev]`.
- **Seeder can't reach the engine** → start it first (`python -m scp_memory`) or use
  `--in-process`.
- **Why is everything "fresh" / why doesn't light-mode rank above dark-mode on the engine?**
  → the engine sets `recorded_at = now` and uses a hermetic stand-in embedder, so the
  freshness/ranking demo is muted there. Trust *scores* are still meaningful. See the Android
  app (backdated) or real embeddings for the ranking effect.
- **Is this production-ready?** → the engine, SDKs, and console are built to production
  patterns (tests, SLOs, audit, modularity). The *defaults* are demo-grade on purpose;
  flip the opt-in backends for real deployments.
- **Where do I report the design rationale for X?** → [`documents/06-adr-collection.md`](documents/06-adr-collection.md).

## 13. Where to go next

- **Understand the vision:** [`documents/04-engineering-thesis.md`](documents/04-engineering-thesis.md)
- **Understand the system:** [`documents/05-architecture-document.md`](documents/05-architecture-document.md)
- **See the decisions:** [`documents/06-adr-collection.md`](documents/06-adr-collection.md)
- **Read the deep dives:** [`blog_series/`](blog_series/)
- **Contribute:** start from the roadmap [`documents/13-future-roadmap.md`](documents/13-future-roadmap.md).

Welcome aboard. If you can run the engine and seed the 10 golden examples, you understand
80% of what makes this project different — the rest is depth.
