# SCP Memory Engine — Leverage Artifacts

> The **20% of artifacts that create 80% of the long-term value** from
> `scp-memory-core` — optimized as a **Principal-level hiring signal** for FAANG
> and senior infrastructure roles.

This folder is the strategic layer on top of the engineering work. The code proves
you can build a trust-aware memory layer; these documents make that work **legible,
discoverable, and credible** to hiring committees, open-source users, and founders.

## How to read this folder

| # | File | What it is | Primary audience |
|---|---|---|---|
| — | [`README.md`](README.md) | This index | You |
| 00 | [`00-project-analysis.md`](00-project-analysis.md) | Core innovation, complexity, differentiators, career/startup signal | You / strategists |
| 01 | [`01-artifact-inventory.md`](01-artifact-inventory.md) | The full universe of possible artifacts | You |
| 02 | [`02-pareto-ranking.md`](02-pareto-ranking.md) | Every artifact scored on leverage | You |
| 03 | [`03-the-80-20-artifact-set.md`](03-the-80-20-artifact-set.md) | The 10 chosen high-ROI artifacts | You |
| 04 | [`04-engineering-thesis.md`](04-engineering-thesis.md) | The vision / "why this matters" essay | Hiring committees, founders |
| 05 | [`05-architecture-document.md`](05-architecture-document.md) | System design of record | Staff/Principal reviewers |
| 06 | [`06-adr-collection.md`](06-adr-collection.md) | Top 10 architecture decisions | Engineers, interviewers |
| 07 | [`07-readme-positioning.md`](07-readme-positioning.md) | OSS positioning + messaging | GitHub visitors |
| 08 | [`08-benchmark-report.md`](08-benchmark-report.md) | Methodology + results framework | Skeptical engineers |
| 09 | [`09-principal-engineer-case-study.md`](09-principal-engineer-case-study.md) | Interview-grade narrative | Hiring committees |
| 10 | [`10-blog-series-plan.md`](10-blog-series-plan.md) | Editorial plan for `/blog_series` | You |
| 11 | [`11-demo-and-examples-pack.md`](11-demo-and-examples-pack.md) | The 10 golden examples + demo scripts | Users, reviewers |
| 12 | [`12-talk-and-presentation-deck.md`](12-talk-and-presentation-deck.md) | Conference talk outline | Conference CFPs |
| 13 | [`13-future-roadmap.md`](13-future-roadmap.md) | 3 / 6 / 12-month roadmap | Users, contributors, recruiters |
| 14 | [`14-reusable-asset-catalog.md`](14-reusable-asset-catalog.md) | Patterns extractable to other projects | You |
| 15 | [`15-career-leverage-analysis.md`](15-career-leverage-analysis.md) | How to convert this into offers | You |
| 16 | [`16-startup-leverage-analysis.md`](16-startup-leverage-analysis.md) | PMF, moat, monetization | You / co-founders |
| 17 | [`17-30-day-execution-plan.md`](17-30-day-execution-plan.md) | What to do next, 3 hrs/day | You |

## The shared dataset

[`golden-examples.json`](golden-examples.json) is the **single source of truth** for
the 10 golden examples. Two seeders consume it:

- **Engine:** `../seed/seed_golden_examples.py` → POSTs to the running engine; verify
  in the Admin Console (Memory Explorer) or via `GET /v1/memories`.
- **Android:** `../../SCPMemoryEngine_AndroidReferenceApp/seed/seed_golden_device.py`
  → writes the device Room DB; verify on the app's Explore screen.

See [`11-demo-and-examples-pack.md`](11-demo-and-examples-pack.md) for run + verify
instructions.

## Source of truth

These documents **summarize and package** the engineering already recorded in
[`../project-memory-bank/`](../project-memory-bank/). Where they disagree, the memory
bank wins — it is the operational record; this folder is the narrative on top of it.
