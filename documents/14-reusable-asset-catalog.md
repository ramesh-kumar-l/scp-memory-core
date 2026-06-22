# 14 — Reusable Asset Catalog

> **Step 6.** The patterns, templates, and frameworks extracted from this project that are
> reusable across *other* projects — the compounding-learning artifact. Each entry: what it
> is, where it lives here, how to reuse it.

---

## Architectural patterns

| Asset | What it is | In this repo | Reuse it for |
|---|---|---|---|
| **Decomposable trust score** | A scalar built from named, inspectable sub-scores + a human explanation, never a black box | `trust/` (provenance/confidence/freshness/explain) | Any ranking/scoring system that must be auditable (fraud, relevance, risk) |
| **Explainability-as-contract** | Response *always* carries per-signal scores + weights + rationale | `/v1/retrieval/search` shape | Any ML-backed API where "why" matters |
| **Backend seam + factory** | Swap implementations by env var behind a stable interface | `embedder_factory`, `keyword_backend`, vector backends, `RelationDetector` | Laptop→cluster portability without forking the contract |
| **Hermetic default / pluggable scale** | Zero-dependency offline default; real infra opt-in | SQLite/brute-force/BM25/hashing defaults | Any OSS infra that must clone-and-run in CI |
| **Relational-truth + derived index** | Transactional store is canonical; vector/keyword indexes are rebuildable projections | services + write-through | Any system mixing a DB with a search index |
| **Calibration gate** | A model change must pass an offline metric (Brier/ECE) before shipping | `evals/run_trust_calibration.py` + ADR-06 | Gating any model/heuristic swap on a measured property |

## Engineering / process patterns

| Asset | What it is | Reuse it for |
|---|---|---|
| **Memory-bank operating model** | A 29-file, numbered, cross-linked project brain read before every task; phase-with-exit-criteria + a stop rule | Running any solo or small-team project with team-grade legibility |
| **Strict modularity (<300 lines)** | Hard per-file cap forcing single responsibility | Keeping any codebase reviewable and contributor-friendly |
| **Phase + exit-criteria delivery** | One active phase, explicit done-conditions, stop-and-confirm boundaries | Avoiding scope creep on long solo builds |
| **Hermetic eval harnesses** | Fixed labelled datasets, deterministic, no network (nDCG/MRR; Brier/ECE) | Making "is it actually better?" answerable and CI-able |

## Reusable templates (lift these directly)

- **ADR template** — Decision · Alternatives · Rationale · Consequences (see [`06`](06-adr-collection.md)).
- **Benchmark report template** — Metrics · Methodology · Baselines · Results (measured vs
  TODO) · Conclusions · Reproduce (see [`08`](08-benchmark-report.md)).
- **Case-study template** — Problem · Constraints · Architecture · Tradeoffs · Impact ·
  Lessons + an interview-usage map (see [`09`](09-principal-engineer-case-study.md)).
- **Blog-post skeleton** — Hook · Vivid problem · Design+diagram+rejected alternative ·
  Code/output · Tradeoffs · CTA (see [`10`](10-blog-series-plan.md)).
- **Pareto artifact-selection template** — inventory → 6-axis scoring → leverage = value/effort
  → mandatory-category check (this whole `/documents` folder is the worked example).
- **Golden-dataset pattern** — one JSON source of truth → multiple seeders, each example
  tagged with what it *demonstrates* (see [`golden-examples.json`](golden-examples.json)).

## Prompt / collaboration assets

- **The Pareto leverage prompt** (the one that generated this folder) — a reusable meta-prompt
  for turning *any* finished project into its highest-leverage artifact set.
- **"Clarify before implementing"** gate — front-load ambiguous decisions (DB target,
  audience, depth) as explicit questions before generating volume.

## How to package these for reuse

1. Extract the templates above into a personal `engineering-templates/` repo.
2. Keep the **memory-bank operating model** as a starter kit (numbered file scaffold).
3. Turn the **decomposable-trust** and **explainability-as-contract** patterns into a short
   reference doc you can cite in design reviews.

> The meta-point for a Principal portfolio: you didn't just build a system, you produced
> **reusable methodology** — patterns, templates, and an operating model others can adopt.
> That transferability is the difference between "good engineer" and "force multiplier."
