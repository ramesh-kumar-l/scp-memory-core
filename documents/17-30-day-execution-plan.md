# 17 — 30-Day Execution Plan

> **Step 9.** What to actually do next, at **3 hours/day**, for maximum leverage. Assumes
> the engineering is largely done; the work now is **packaging, proof, and distribution.**
> Each week ends on an observable signal, matching the project's exit-criteria operating
> model.

---

## Operating principle

You are no longer in build mode; you're in **leverage mode**. Resist new features. The job
is to make the existing work *legible, runnable, and discoverable*. Every task below either
produces a public artifact or removes friction between a stranger and a ⭐.

## Week 1 — Polish the spine + make it runnable (the storefront)

**Goal:** a stranger can land on the repo, understand it in 60 seconds, and run the demo.

| Day | Task (≈3 hrs) | Output |
|---|---|---|
| 1 | Rewrite root `README.md` from [`07`](07-readme-positioning.md): hero, features, one-command quick start, comparison table | Production README |
| 2 | Finish + run the 10 golden examples engine seeder; verify in the console | `seed/seed_golden_examples.py` working end-to-end |
| 3 | Record the **demo GIF** (console retrieval inspector: trust score bars + contradiction query) | Hero GIF in README |
| 4 | Fill the **latency table** in [`08`](08-benchmark-report.md) from a real `/metrics` run | Benchmark report complete |
| 5 | Final pass on the **engineering thesis** + **case study**; link from README | Narrative spine public |
| 6–7 | Buffer / Android device verification of the golden examples | Phase 8 demo-ready |

**Week-1 signal:** clone → `pip install -e .` → `python seed/seed_golden_examples.py` →
see trust scores. No questions asked.

## Week 2 — Proof + first publish (credibility)

**Goal:** the skeptic is answered and the SDKs are installable.

| Day | Task | Output |
|---|---|---|
| 8 | Run NLI through the calibration harness; record before/after ECE | Calibration result (adopt or not, per ADR-06) |
| 9 | Publish **Python SDK** to PyPI (runbook exists) | `pip install scp-memory-sdk` |
| 10 | Publish **TypeScript SDK** to npm | `npm i @scp/memory-sdk` |
| 11–12 | Write + polish **blog post #1** ("Why agents need a memory layer") | `blog_series/01` published-ready |
| 13 | Set up cross-posting (Medium + dev.to canonical), social preview images | Distribution rails |
| 14 | Buffer / draft the launch thread | Launch assets staged |

**Week-2 signal:** SDKs installable; blog #1 + benchmark prove the claims.

## Week 3 — Launch + momentum (distribution)

**Goal:** put it in front of people and start the writing flywheel.

| Day | Task | Output |
|---|---|---|
| 15 | **Launch:** Show HN + r/MachineLearning + LinkedIn/X thread, anchored on blog #1 + GIF | First wave of traffic/stars |
| 16 | Respond to all feedback; file issues; triage | Engagement + roadmap input |
| 17–18 | Publish **blog post #2** (trust as a first-class signal) | Series momentum |
| 19 | Submit the **talk** ([`12`](12-talk-and-presentation-deck.md)) to 2–3 CFPs/meetups | Talk in the pipeline |
| 20 | Add `good-first-issue`s + `CONTRIBUTING.md` | Contributor on-ramp |
| 21 | Buffer / publish **blog post #3** (explainable hybrid retrieval) | 3 posts live |

**Week-3 signal:** public launch done; ≥3 posts live; a talk submitted; first external
engagement.

## Week 4 — Convert + compound (career + optionality)

**Goal:** turn the body of work into interview and career assets, and read the PMF signals.

| Day | Task | Output |
|---|---|---|
| 22 | Update **resume** with the quantified bullets ([`15`](15-career-leverage-analysis.md)) | Principal-framed resume |
| 23 | Update **LinkedIn** (headline, featured, thesis post) | Discoverable profile |
| 24 | Rehearse the **system-design interview narrative** (retrieval + trust + calibration gate) | Interview-ready |
| 25–26 | Publish **blog post #4** (memory lifecycle); reply in the launch thread | 4 posts live |
| 27 | Review **PMF signals** ([`16`](16-startup-leverage-analysis.md)); note any enterprise pull | Go/no-go input on startup option |
| 28 | Retro + update the memory bank (`07`/`08`/`28`); plan the next 30 days | Closed loop |
| 29–30 | Buffer / publish **blog post #5** (calibrate before you sophisticate) | 5 posts live |

**Week-4 signal:** resume + LinkedIn updated, interview narrative rehearsed, 5 posts live,
PMF read taken.

---

## What NOT to do this month

- ❌ Build new engine features (the leverage is in packaging, not code).
- ❌ Stand up a docs site / community infra (premature — needs the traffic first).
- ❌ Chase a perfect benchmark — *directional + honest* beats *delayed*.
- ❌ Start the startup before the PMF signals fire — keep it an option.

## The one-sentence plan

**Week 1 make it runnable, Week 2 make it proven, Week 3 make it seen, Week 4 make it
yours** — then decide, from real signals, whether the next 30 days are more career or more
company.
