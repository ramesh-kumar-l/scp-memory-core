# 03 — The 80/20 Artifact Set

The **10 artifacts** that produce ~80% of the long-term leverage. Each maps to a detailed
outline file in this folder and satisfies the mandatory-category rule (Architecture,
Engineering, Career, Distribution, Open Source, Learning all covered).

| # | Artifact | Category | File | Priority |
|---|---|---|---|---|
| 1 | Engineering Thesis | Research/Career | [`04`](04-engineering-thesis.md) | P0 |
| 2 | Architecture Document | Architecture | [`05`](05-architecture-document.md) | P0 |
| 3 | ADR Collection (Top 10) | Architecture | [`06`](06-adr-collection.md) | P0 |
| 4 | Open-Source README + positioning | Open Source/Distribution | [`07`](07-readme-positioning.md) | P0 |
| 5 | Benchmark Report | Engineering | [`08`](08-benchmark-report.md) | P1 |
| 6 | Principal Engineer Case Study | Career | [`09`](09-principal-engineer-case-study.md) | P0 |
| 7 | Blog Series (6–8 posts) | Distribution | [`10`](10-blog-series-plan.md) → `/blog_series` | P1 |
| 8 | Demo & Examples Pack (10 golden) | Engineering/Distribution | [`11`](11-demo-and-examples-pack.md) | P0 |
| 9 | Talk / Presentation Deck | Distribution/Career | [`12`](12-talk-and-presentation-deck.md) | P2 |
| 10 | Future Roadmap | Product/Open Source | [`13`](13-future-roadmap.md) | P1 |

Plus three cross-cutting deliverables that the prompt requires and that bind the set
together:

- **Reusable Asset Catalog** → [`14`](14-reusable-asset-catalog.md) (Learning)
- **Career Leverage Analysis** → [`15`](15-career-leverage-analysis.md)
- **Startup Leverage Analysis** → [`16`](16-startup-leverage-analysis.md)
- **30-Day Execution Plan** → [`17`](17-30-day-execution-plan.md)

---

## Per-artifact rationale

### 1 — Engineering Thesis · `Why it matters`
The single most reusable asset: it is the source narrative for the README hero, the case
study, every blog intro, and the talk abstract. Audience: hiring committees + founders.
**ROI:** very high. **Effort:** low–medium (1–2 sessions). **Priority:** P0.

### 2 — Architecture Document · `Why it matters`
The artifact a Staff/Principal interviewer asks for. Demonstrates systems judgment:
seams, tradeoffs, scaling, reliability. Audience: senior engineers. **ROI:** high.
**Effort:** medium. **Priority:** P0.

### 3 — ADR Collection · `Why it matters`
Shows *how you decide*, not just what you built — the clearest Principal signal and a
strong interview prop ("walk me through a hard decision"). Audience: engineers,
interviewers. **ROI:** high. **Effort:** medium. **Priority:** P0.

### 4 — Open-Source README + positioning · `Why it matters`
The storefront. Determines whether a GitHub visitor stays 10 seconds or 10 minutes.
Gateway to every star, user, and inbound recruiter. Audience: GitHub visitors. **ROI:**
very high. **Effort:** low–medium. **Priority:** P0.

### 5 — Benchmark Report · `Why it matters`
Converts claims ("explainable", "trustworthy") into **numbers** (nDCG/MRR, Brier/ECE,
p95 latency). Pre-empts the skeptical-engineer objection. Audience: skeptics. **ROI:**
high. **Effort:** medium. **Priority:** P1.

### 6 — Principal Engineer Case Study · `Why it matters`
The highest leverage-per-effort artifact: directly usable in interviews, performance
packets, and promotion cases. Audience: hiring committees. **ROI:** very high. **Effort:**
low. **Priority:** P0.

### 7 — Blog Series · `Why it matters`
The distribution engine. 6–8 in-depth posts with mermaid diagrams drive repo visibility
and establish thought leadership — the FAANG-visibility goal. Audience: HN/Medium/dev.to.
**ROI:** very high (compounding). **Effort:** high. **Priority:** P1.

### 8 — Demo & Examples Pack (10 golden) · `Why it matters`
Turns "read about it" into "run it in one command and *see* the trust scores." The 10
examples are designed to each showcase a differentiator and are seeded into both the
engine DB and the Android device DB. Audience: users, reviewers. **ROI:** high. **Effort:**
medium. **Priority:** P0.

### 9 — Talk / Presentation Deck · `Why it matters`
Unlocks conference CFPs and meetup talks — high-bandwidth visibility and a durable
authority signal. Audience: conference organizers, live audiences. **ROI:** medium–high.
**Effort:** medium. **Priority:** P2.

### 10 — Future Roadmap · `Why it matters`
Signals momentum and vision (not a dead repo). Converts visitors into contributors and
gives recruiters a "where this is going" story. Audience: contributors, recruiters.
**ROI:** medium. **Effort:** low. **Priority:** P1.

---

## What we deliberately cut

- **Docs site, community infra, pricing doc, security white paper, SDK reference docs:**
  high absolute value but premature — they presuppose traffic the top 10 must first
  create. Scheduled post-launch in [`13`](13-future-roadmap.md).
- **Resume/LinkedIn/launch thread:** kept as cheap *finishers* derived from the case
  study + README, sequenced in the [30-day plan](17-30-day-execution-plan.md) rather than
  built as standalone primary artifacts.

This is the Pareto cut: **narrative spine + distribution surface + one proof artifact**,
nothing speculative.
