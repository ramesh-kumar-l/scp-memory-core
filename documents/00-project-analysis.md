# 00 — Project Analysis

**Project:** SCP Memory Engine (`scp-memory-core`)
**Framing for:** Principal-level engineering signal · Primary objective: CAREER (FAANG-visible), with startup optionality
**Stage:** Working system — Phases 1–7 complete (engine + 2 SDKs + admin console + production hardening); Phase 8 (Android reference app) in progress.

---

## 1. Core innovation

Most "AI memory" today is a **vector index with a CRUD wrapper**: store embeddings,
nearest-neighbor at query time, hope the top-k is relevant. SCP Memory Engine reframes
memory as **managed infrastructure** with three properties that vector DBs do not
provide:

1. **Trust as a first-class, decomposable signal.** Every memory carries a trust score
   built from **provenance** (who said it — user 1.0 → consolidation 0.75 → inferred
   0.5 → system 0.4), **confidence** (raised by corroboration, lowered by
   contradiction), and **freshness** (type-aware exponential decay: an `event` half-life
   ~14 days ≫ a `preference` ~180 days). Trust is the **4th ranking dimension**, not a
   bolt-on.
2. **Explainability as a contract guarantee.** Every retrieval result *always* carries
   per-signal scores (`keyword`, `vector`, `metadata`, `importance`, `trust`), the fusion
   weights in effect, and a human-readable trust explanation. You can always answer *"why
   did this memory surface, and should I believe it?"*
3. **Memory lifecycle / intelligence.** Memories are not static rows: importance scoring,
   deduplication, **consolidation** (summaries with `derived_from` provenance), and
   **decay** are managed passes — the substrate a long-lived agent needs but a vector
   store never had.

The thesis in one line: **a memory layer that an agent — and an auditor — can trust and
explain, not just retrieve from.**

## 2. Technical complexity

- **Hybrid retrieval pipeline:** metadata filter → (BM25 keyword ∪ vector ANN)
  candidates → weighted/RRF fusion → rank → attach trust. Each stage is pure and
  independently testable; fusion is a swappable strategy.
- **Pluggable backends behind seams:** embeddings (`HashingEmbedder` hermetic default →
  opt-in sentence-transformers), keyword (in-process BM25 → SQLite FTS5 → Postgres
  tsvector), vector (brute-force → Qdrant), trust relation detection (lexical → opt-in
  NLI cross-encoder). The default path is **hermetic and offline** so CI never needs a
  network or a GPU.
- **Production surface:** FastAPI + Pydantic v2 + SQLAlchemy 2.x; Prometheus `/metrics`,
  opt-in OpenTelemetry tracing with per-stage spans, JSON logs with trace correlation,
  readiness checks, severity-routed Alertmanager rules.
- **Two SDKs** (sync Python over httpx; TypeScript over Fetch) and an **admin console**
  (Vite + React) that renders the entire signal surface.
- **Calibration discipline:** a trust-calibration harness (Brier/ECE) **gates** swapping
  the lexical detector for NLI — a model change must *measurably* improve calibration
  before it ships.
- **Strict modularity:** every source file < 300 lines; 132 Python tests + SDK/console
  tests; `ruff`/`black` clean.

## 3. Differentiators

| Axis | Vector DB / RAG lib | Agent-memory libs | **SCP Memory Engine** |
|---|---|---|---|
| Retrieval | Vector only | Vector + recency | **Hybrid + explainable per-signal** |
| Trust | None | Implicit/recency | **Decomposable provenance+confidence+freshness** |
| Explainability | None | Limited | **Contract guarantee on every result** |
| Lifecycle | None | Summarize | **Importance, dedup, consolidate, decay** |
| Governance | Varies | Rare | **Namespacing, append-only audit, governed delete** |
| Operability | Library | Library | **Metrics, traces, SLOs, alerts, readiness** |

The combination — **trust + explainability + governance + operability** in one coherent
contract — is the differentiated position. Each piece exists somewhere; the *integration*
is the moat.

## 4. Market relevance

AI is moving from stateless prompt→response to **long-lived agents**. Long-lived agents
need durable, trustworthy, auditable memory. The current answer ("just add a vector DB")
is insufficient the moment an agent must (a) reconcile contradictory facts, (b) explain a
decision to a human, or (c) satisfy a compliance/audit requirement. That gap is exactly
the SCP surface. Timing is strong: agent frameworks are proliferating, but **shared
memory *infrastructure* with trust and governance does not yet exist as a standard.**

## 5. Career signal value (Principal lens)

This project demonstrates the Principal-level competencies that are hard to fake:

- **Category-level thinking:** named a new layer ("trust-aware memory infrastructure")
  rather than building a feature.
- **Architecture under constraint:** pluggable seams, hermetic defaults, contract
  stability across model swaps — choices that show systems judgment, not just coding.
- **Operational maturity:** SLOs, alerts, calibration gates, append-only audit.
- **Breadth + depth:** backend engine, two SDKs, a web console, an Android client, and a
  benchmark/eval discipline — end-to-end ownership.
- **Written communication:** a 29-file memory bank, ADRs, and this artifact set — the
  Principal "force multiplier through writing" signal.

## 6. Startup potential

Plausible as **open-core infrastructure**: OSS engine for adoption; managed/hosted memory
service + governance/compliance features as the commercial layer. The moat is integration
depth + trust/governance + an explainability contract that's painful to retrofit. (Full
analysis in [`16-startup-leverage-analysis.md`](16-startup-leverage-analysis.md).)

## 7. Open-source potential

High. Clear category, hermetic offline default (one-command demo), explainable output
that *shows well in screenshots and GIFs*, and a console that makes the value visible
without reading code. The 10 golden examples + blog series are designed to convert a
GitHub visitor into a star, then a user, then a contributor.

---

## Summary

`scp-memory-core` is a **working, operable, explainable trust-aware memory layer** —
not a demo. Its differentiation is *integration* (trust + explainability + governance +
ops in one contract), its timing rides the long-lived-agent wave, and its breadth +
written rigor make it an unusually strong **Principal-level hiring signal** with credible
startup optionality. The leverage now is not more code — it's **packaging the work so the
right people see it.**
