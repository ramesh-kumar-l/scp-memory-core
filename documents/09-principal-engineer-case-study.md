# 09 — Principal Engineer Case Study

> **Artifact 6 of the 80/20 set** — and the highest leverage-per-effort. Directly reusable
> in interviews, promotion packets, and performance reviews. Format mirrors how a hiring
> committee reads impact: Problem · Constraints · Architecture · Tradeoffs · Impact ·
> Lessons.

---

## Title

**Designing a Trust-Aware Memory Layer for Long-Lived AI Agents**

## Problem

Long-lived AI agents accumulate memory, and the default solution — a vector database — has
no notion of *trust*, *explanation*, or *governance*. An agent could not tell a
user-confirmed fact from a model's stale guess, could not explain why a memory surfaced, and
had no audit trail when memory touched a real user. I set out to build a **memory
infrastructure layer** that treats trust and explainability as contract guarantees, not
features — runnable offline by a newcomer, yet operable at scale.

## Constraints

- **Hermetic by default** — must clone-and-run with no GPU, no network, no external service;
  CI must be deterministic.
- **Contract stability** — clients (two SDKs, a web console, an Android app) must not break
  when the implementation swaps a model or a backend.
- **Governance non-negotiable** — namespacing, append-only audit, governed delete from day
  one.
- **Strict modularity** — every file < 300 lines; single responsibility throughout.
- **Solo, phased delivery** — one phase active at a time, each with explicit exit criteria,
  recorded in a 29-file memory bank that is the operating source of truth.

## Architecture

A FastAPI engine with a **pure, I/O-free core** (retrieval + trust) wrapped by services that
own persistence. The **relational store is the source of truth**; the vector index is a
rebuildable projection. Retrieval is a pipeline — metadata filter → (BM25 keyword ∪ vector
ANN) → weighted fusion → rank → **attach trust** — and every result carries per-signal
scores, fusion weights, and a decomposable trust breakdown (provenance × confidence ×
freshness). Scale paths (Postgres, Qdrant, FTS5/tsvector, NLI) sit **behind seams** selected
by env vars, with the API contract unchanged. (Full design: [`05`](05-architecture-document.md);
decisions: [`06`](06-adr-collection.md).)

## Tradeoffs I owned

1. **Relational truth over vector-primary** — accepted write-through/reconciliation
   complexity to get correctness, audit, and governed delete. The index is disposable; the
   record is not. *(ADR-01)*
2. **Explainability as an always-on contract** — accepted larger payloads and stricter typing
   so "why did this surface?" is never a second query. *(ADR-02)*
3. **Calibration gate over model sophistication** — built a Brier/ECE harness and refused to
   default to an NLI detector until it *measurably* improves calibration. A smarter model that
   is worse calibrated makes trust less trustworthy. *(ADR-06)* This is the decision I'd lead
   with in an interview: it shows I optimize for the *property the user cares about*
   (well-calibrated trust), not the impressive-sounding component.
4. **Hermetic defaults over realistic defaults** — chose a hashing embedder and lexical trust
   as defaults to keep onboarding and CI frictionless, and documented the opt-in path to real
   quality so no one mistakes the demo for the ceiling. *(ADR-04)*

## Impact

- A **working, operable** memory engine: 132 Python tests, two SDKs, an admin console, an
  Android reference client; `ruff`/`black` clean; strict modularity held (largest engine file
  192 lines).
- **Measured discipline:** weighted fusion validated over RRF by benchmark (nDCG 1.00 vs
  0.69); trust calibration quantified (Brier ≈ 0.17 / ECE ≈ 0.19) with the over-confidence
  failure mode identified and an upgrade path gated on improvement.
- **A reusable design** for memory-as-infrastructure — the trust model, the explainability
  contract, and the seam pattern transfer beyond this repo.
- **A communication artifact set** (this folder + a blog series + a talk) that makes the work
  legible to engineers, users, and committees.

## Lessons learned

- **Contracts are the real product.** Stable response shapes across model/backend swaps were
  worth more than any single implementation choice — they let four clients exist without
  coupling.
- **Calibrate before you sophisticate.** The instinct to "just use NLI" was wrong until proven
  on calibration. Gates beat vibes.
- **Hermetic defaults are an adoption strategy.** The one-command, offline demo is the
  difference between a repo people *star* and one they *run*.
- **Write it down as you go.** The memory bank turned a solo project into something with the
  legibility of a team codebase — and made artifacts like this one nearly free to produce.

---

## Interview usage map

| Prompt | Lead with |
|---|---|
| "Tell me about a hard technical decision." | The **calibration gate** (ADR-06) |
| "Design a system for X at scale." | The **seam/backends** pattern + relational-truth |
| "Tell me about a tradeoff you regret / would revisit." | Hermetic defaults vs realistic quality |
| "How do you ensure quality?" | Eval harnesses + append-only audit + strict modularity |
| "Show technical leadership without a team." | The phased operating model + memory bank + this artifact set |

**Quantified resume bullets (derive from this):**
- *Designed and built a trust-aware memory infrastructure layer (FastAPI/Pydantic/SQLAlchemy)
  with explainable hybrid retrieval and a decomposable trust model; 132 tests, two SDKs, a web
  console, and an Android client, all on a stable API contract.*
- *Introduced a calibration gate (Brier/ECE) that blocks model swaps unless they measurably
  improve trust calibration; validated weighted fusion over RRF by benchmark (nDCG 1.00 vs
  0.69).*
- *Held strict modularity (<300 lines/file) and a hermetic, one-command offline default across
  the engine, SDKs, and console.*
