# 10 — Blog Series Plan

> **Artifact 7 of the 80/20 set.** The distribution engine and the FAANG-visibility play.
> This is the editorial plan; the full publish-ready posts live in
> [`../blog_series/`](../blog_series/), each with mermaid diagrams and code.

---

## Strategy

- **Goal:** establish thought leadership in "agent memory," drive stars/traffic to the repo,
  and create a durable, linkable body of work that recruiters and engineers find.
- **Voice:** senior engineer explaining hard tradeoffs plainly — opinionated, concrete,
  diagram-first. No hype; every claim links to code or a benchmark.
- **Format:** 1,500–2,500 words, ≥1 mermaid diagram each, runnable snippets, a clear CTA to
  the repo and the next post. Cross-post Medium + dev.to; syndicate to a launch thread.
- **Cadence:** one post / week over ~7 weeks. Post #1 anchors a Show HN / r/MachineLearning
  launch.

## The series (publishing order)

| # | Title | Hook / thesis | Key diagram | File |
|---|---|---|---|---|
| 1 | **Why AI Agents Need a Memory Layer, Not a Bigger Vector Index** | The category argument; the 3 failures of vector-as-memory | Stateless→agent + the gap | `blog_series/01-why-agents-need-a-memory-layer.md` |
| 2 | **Designing Trust as a First-Class Signal in Agent Memory** | Provenance × confidence × freshness, decomposable | Trust decomposition tree | `blog_series/02-trust-as-a-first-class-signal.md` |
| 3 | **Explainable Hybrid Retrieval You Can Actually Debug** | keyword ∪ vector ∪ metadata + visible per-signal scores | Retrieval sequence | `blog_series/03-explainable-hybrid-retrieval.md` |
| 4 | **Memory Has a Lifecycle: Importance, Dedup, Consolidation, Decay** | Memory isn't write-once; the intelligence passes | Lifecycle state machine | `blog_series/04-memory-lifecycle.md` |
| 5 | **Calibrate Before You Sophisticate: Gating Model Swaps with Brier & ECE** | Why a smarter model can make trust worse | Calibration gate flow | `blog_series/05-calibrate-before-you-sophisticate.md` |
| 6 | **Hermetic by Default, Pluggable at Scale: Backend Seams Done Right** | One codebase laptop→cluster; the seam pattern | Seam/backends diagram | `blog_series/06-hermetic-by-default-pluggable-at-scale.md` |
| 7 | **Governing Agent Memory: Namespacing, Audit, and the Right to Be Forgotten** | Memory that touches real users needs governance | Audit/delete flow | `blog_series/07-governing-agent-memory.md` |

> Optional #8 (founder angle): *"Memory as Infrastructure: The Open-Core Opportunity"* —
> defer unless pursuing the startup track; overlaps [`16`](16-startup-leverage-analysis.md).

## Per-post skeleton (applied in each file)

1. **Hook** — a concrete failure or surprising claim (≤150 words).
2. **The problem, made vivid** — a scenario the reader recognizes.
3. **The design** — diagram + the decision + the rejected alternative (pull from the ADRs).
4. **Show the code/output** — a runnable snippet and a real response shape.
5. **Tradeoffs / limits** — what it costs, what it doesn't solve (honesty = credibility).
6. **CTA** — run the demo, ⭐ the repo, read the next post.

## Reuse map (write once, use everywhere)

- Post 1 ← [`04-engineering-thesis.md`](04-engineering-thesis.md)
- Posts 2,5 ← [`06-adr-collection.md`](06-adr-collection.md) (ADR-03, ADR-06) + [`08`](08-benchmark-report.md)
- Post 3 ← [`05-architecture-document.md`](05-architecture-document.md) (retrieval sequence)
- Post 6 ← ADR-04/05; Post 7 ← ADR-08
- All ← the 10 golden examples ([`11`](11-demo-and-examples-pack.md)) for concrete payloads.

## Distribution checklist (per post)

- [ ] Canonical on personal blog / Medium; mirror to dev.to with `canonical_url`.
- [ ] Repo link in first and last paragraph; one diagram as the social preview image.
- [ ] Tags: `ai`, `llm`, `agents`, `machine-learning`, `software-architecture`.
- [ ] Post 1 → Show HN + LinkedIn/X thread; subsequent posts → reply in the thread.
- [ ] Add each to the repo `README` "Writing" section and [`26-public-artifacts`].
