# 13 — Future Roadmap

> **Artifact 10 of the 80/20 set.** Signals momentum and vision — converts visitors into
> contributors and gives recruiters a "where this is going" story. Horizons are outcome-
> framed, not a feature dump. Aligns with [`../project-memory-bank/23-roadmap.md`].

---

## Now (shipped, Phases 1–7 + hardening)

Trust-aware engine · explainable hybrid retrieval · memory lifecycle · two SDKs · admin
console · observability stack · calibration + retrieval eval harnesses · pluggable backend
seams. Phase 8 (Android reference app) in progress.

## Next 3 months — *Make it real and discoverable*

**Theme: from "works on my machine" to "others run and trust it."**

- **Finish + verify Phase 8** — device build/run, the 10 golden examples on-device, a demo
  GIF/video.
- **Real semantic quality on the opt-in path, measured** — run the NLI detector through the
  calibration harness; adopt only if ECE drops (ADR-06). Publish the before/after.
- **Latency benchmark, filled in** — real p50/p95/p99 numbers in [`08`](08-benchmark-report.md)
  and the console Benchmarks screen.
- **Publish the SDKs** — PyPI + npm (packaging is ready; runbook exists).
- **Launch** — blog post #1 + Show HN + the README hero GIF; ship posts 2–3.
- **Async Python client** — currently deferred; needed for serious adopters.

*Exit signal:* a stranger clones, runs the 10 examples, sees trust scores, and stars —
without asking you anything.

## Next 6 months — *Make it adoptable at scale*

**Theme: production paths and ecosystem fit.**

- **Production-validate the scale backends** — Postgres + Qdrant + tsvector beyond CI;
  document deployment topologies and a real load test.
- **Framework adapters** — thin integrations so popular agent frameworks can use SCP as
  their memory backend (the contract is already framework-agnostic).
- **A real NLI/embedding default tier** with a model card and the calibration evidence.
- **Docs site** — from the memory bank + this folder (the content already exists).
- **Governance deep-dive** — multi-tenant isolation tests, retention policies, a
  right-to-be-forgotten walkthrough (blog #7 → feature hardening).
- **Community on-ramp** — `good-first-issue` set, contribution guide, Discussions.

*Exit signal:* one external project uses SCP as its memory layer; one external contributor
merges a PR.

## Next 12 months — *Make it a standard candidate*

**Theme: category leadership + optionality.**

- **A proposed "agent memory response" contract** — formalize the signals + trust + audit
  shape as something portable across frameworks; invite feedback.
- **Trust research line** — better corroboration/contradiction detection, calibration across
  domains, published with reproducible evals.
- **Hosted/managed reference** (if pursuing the startup track) — open-core boundary per
  [`16`](16-startup-leverage-analysis.md): OSS engine, managed memory + governance/compliance
  as the commercial layer.
- **Talks + writing flywheel** — deliver the conference talk ([`12`](12-talk-and-presentation-deck.md));
  the series becomes a reference people cite.

*Exit signal:* "trust-aware memory" is a phrase others use, and this repo is what they link.

---

## How the horizons map to leverage

| Horizon | Career signal | OSS signal | Startup signal |
|---|---|---|---|
| 3 mo | Shipped + measured + launched | Stars, runnable demo | Validated core |
| 6 mo | Scale + ecosystem ownership | Contributors, adopters | First external user |
| 12 mo | Category authority | Standard candidate | Open-core optionality |

The roadmap is deliberately **outcome-gated, not date-gated** — each horizon ends on a
signal you can observe, matching the project's phase-with-exit-criteria operating model.
