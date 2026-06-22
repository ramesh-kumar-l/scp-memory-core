# 07 — Open-Source README + Positioning

> **Artifact 4 of the 80/20 set.** The storefront — decides whether a visitor stays 10
> seconds or 10 minutes. This file is the *positioning spec*; the production `README.md`
> at the repo root is the rendered result.

---

## Positioning statement

> **SCP Memory Engine** — a trust-aware, explainable memory layer for long-lived AI agents.
> Not a vector index: a managed memory substrate where every result tells you **why it
> surfaced** and **how much to trust it** — with provenance, corroboration, freshness, and
> an append-only audit trail.

**Tagline options (A/B these):**
1. *"Memory your agent — and your auditor — can trust."*
2. *"The trust layer for AI memory."*
3. *"Explainable, trust-aware memory infrastructure for long-lived agents."*

## Hero section (above the fold)

```
# SCP Memory Engine
Trust-aware, explainable memory infrastructure for long-lived AI agents.

[ badges: license · CI · tests passing · python 3.11+ · ruff/black ]

Every retrieval result carries per-signal scores and a decomposable trust
score (provenance × confidence × freshness) — plus an append-only audit
trail under it all. Runs offline in one command.

  pip install -e .  &&  python examples/quickstart.py

[ ▸ 60-second demo GIF: console showing trust score bars ]
```

The GIF is the single highest-converting asset — it makes "explainable" *visible*. Capture
the admin console's Retrieval Inspector with the per-signal score bars and a trust
explanation. (See [`11-demo-and-examples-pack.md`](11-demo-and-examples-pack.md).)

## Features (lead with differentiators, not the stack)

- 🧠 **Trust as a ranking signal** — provenance × confidence × freshness, decomposable and
  explained on every result.
- 🔍 **Explainable hybrid retrieval** — keyword ∪ vector ∪ metadata, fused with visible
  per-signal scores and weights.
- ♻️ **Memory lifecycle** — importance, dedup, consolidation (with `derived_from`
  provenance), and type-aware decay.
- 🛡️ **Governed by default** — namespacing, append-only audit, soft/hard delete.
- 📈 **Operable** — Prometheus metrics, opt-in OTel traces, SLOs, alert routing, readiness.
- 🧪 **Calibration-gated** — a model swap must measurably improve trust calibration
  (Brier/ECE) before it ships.
- 🔌 **Hermetic default, pluggable scale** — SQLite/brute-force/BM25 out of the box;
  Postgres/Qdrant/FTS5/NLI behind seams.
- 📦 **Two SDKs + admin console + Android reference app.**

## Quick start (must be one command)

```bash
git clone … && cd scp-memory-core
pip install -e .
python examples/quickstart.py            # CRUD + audit, in-process, no server
python examples/retrieval_quickstart.py  # hybrid retrieval with per-signal scores
python examples/trust_quickstart.py      # trust breakdown + explanation
python seed/seed_golden_examples.py      # load the 10 golden examples
```

Full newbie path: [`../Quick_Stater_Guide.md`](../Quick_Stater_Guide.md).

## Examples (show, don't tell)

Link the 10 golden examples and what each *proves* (contradiction, consolidation, decay,
hybrid retrieval, governance) — table from [`11`](11-demo-and-examples-pack.md). Each
example is a screenshot-able moment.

## Architecture (one diagram, link the rest)

Embed the component mermaid diagram from [`05`](05-architecture-document.md); link the full
architecture doc and the ADRs. Visitors who scroll this far are evaluating you as an
engineer — give them the decision log.

## Roadmap (signal momentum)

Three bullets per horizon from [`13-future-roadmap.md`](13-future-roadmap.md) + a link.
Shows the repo is alive and has direction.

## Positioning do / don't

| Do | Don't |
|---|---|
| Lead with **trust + explainability** | Lead with "FastAPI + SQLAlchemy" |
| Show a GIF of trust score bars | Wall of prose before the first command |
| Say "not a vector index" explicitly | Compete on raw vector speed |
| One-command, offline demo | Require Docker/GPU to see value |
| Link ADRs + benchmark for skeptics | Hide the methodology |

## Distribution hooks (built into the README)

- A **"Why not just a vector DB?"** FAQ section → links blog post #1.
- A **comparison table** (from [`00`](00-project-analysis.md)) → answers the first objection.
- Clear **CTA**: ⭐ star, run the demo, read the thesis. Repo description + topics tuned for
  search (`ai-memory`, `agent-memory`, `rag`, `trust`, `explainability`, `llm`).
