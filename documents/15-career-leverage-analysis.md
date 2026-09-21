# 15 — Career Leverage Analysis

> **Step 7.** How to convert this project into interviews, offers, and a promotion case —
> framed for a **Principal** signal aimed at FAANG and senior-infra roles.

---

## The core asset

A working, operable, *explainable* trust-aware memory layer — plus the written record
(memory bank, ADRs, this folder, a blog series). The rare combination here is **systems
depth + operational maturity + communication**. Most candidates show one; Principal
requires all three. Lead with that.

## FAANG / system-design interviews

- **Use it as your "design a system" anchor.** When asked to design memory/RAG/agent
  infrastructure, you're not theorizing — you've *built and benchmarked* it. Whiteboard the
  retrieval pipeline ([`05`](05-architecture-document.md)) and the trust decomposition from
  memory.
- **"Tell me about a hard decision"** → the calibration gate (ADR-06): a real tradeoff, a
  rejected alternative ("just use NLI"), and a consequence you owned. This single story
  signals Principal judgment better than any feature.
- **"How do you ensure quality / make decisions under uncertainty?"** → eval harnesses +
  append-only audit + the benchmark that chose weighted over RRF.
- **Drill-down resilience:** because the core is pure and modular, you can go arbitrarily
  deep on any layer — interviewers reward candidates who don't bottom out.

## Staff vs Principal framing

| | Staff signal | **Principal signal (lead with this)** |
|---|---|---|
| Scope | Built a complex system well | **Named and defined a category** ("trust-aware memory infra") |
| Decisions | Made good tradeoffs | **Built a *gate* so the org makes good tradeoffs repeatedly** (calibration) |
| Influence | Strong execution | **Reusable methodology + writing others adopt** ([`14`](14-reusable-asset-catalog.md)) |
| Communication | Clear docs | **A thesis, ADRs, benchmarks, and a talk** that shape how people think |

## Resume (quantified bullets — from the case study)

- *Designed and built a trust-aware, explainable memory infrastructure layer (FastAPI /
  Pydantic v2 / SQLAlchemy 2.x) with hybrid retrieval and a decomposable trust model; 132
  tests, two SDKs, a web console, and an Android client on a single stable API contract.*
- *Introduced a calibration gate (Brier/ECE) blocking model swaps that don't measurably
  improve trust calibration; validated weighted fusion over RRF by benchmark (nDCG 1.00 vs
  0.69).*
- *Established a hermetic, one-command offline default (SQLite/brute-force/BM25) with
  pluggable Postgres/Qdrant/FTS5/NLI scale paths behind seams.*
- *Held strict modularity (<300 lines/file) across engine, SDKs, and console; full
  observability (Prometheus/OTel/SLOs/alerts) and append-only audit.*

## LinkedIn

- **Headline:** "Building trust-aware memory infrastructure for AI agents | Infra / ML
  platform."
- **Featured:** the repo, blog post #1, and the engineering thesis.
- **Cadence:** one post per blog drop; each opens with the one-paragraph thesis and a diagram.
  Tag the agent/LLM-infra conversation; the goal is for engineers and recruiters to *find*
  you via the content.

## Conference talks & thought leadership

- Submit [`12`](12-talk-and-presentation-deck.md) to AI-infra meetups and PyData/PyCon-class
  CFPs. A recorded talk is simultaneously: a hiring signal, README hero video, and authority
  proof.
- The blog series ([`10`](10-blog-series-plan.md)) is the written half of the same flywheel:
  writing → visibility → inbound → talks → more visibility.

## Technical leadership (without a team)

The phase-with-exit-criteria operating model + the memory bank demonstrate that you can run
a program with team-grade rigor *solo*. That's the hardest leadership signal to fake on a
side project — point to it explicitly.

## The 6-week conversion plan (high level)

1. Polish README + thesis + case study (done in [`/documents`](README.md)).
2. Launch blog #1 + Show HN + the demo GIF.
3. Publish SDKs; ship blogs weekly.
4. Submit one talk.
5. Update resume/LinkedIn with the quantified bullets and links.
6. Let inbound + your applications point at one coherent body of work.

Detailed daily plan: [`17-30-day-execution-plan.md`](17-30-day-execution-plan.md).

> The mistake to avoid: treating this as "a side project I'll mention." It's a **portfolio
> centerpiece and an interview operating system.** Make every interview reference it, and
> make the internet able to find it.
