# 06 — ADR Collection (Top 10)

> **Artifact 3 of the 80/20 set.** How decisions were made, not just what was built — the
> clearest Principal signal and a strong interview prop. Format: Decision · Alternatives ·
> Rationale · Consequences. These consolidate the canonical log in
> [`../project-memory-bank/25-adr-log.md`].

---

### ADR-01 — Relational store is the source of truth; vector is a derived index
- **Decision:** Persist canonical memory state in a relational DB (SQLite → Postgres). The
  vector store is a rebuildable, write-through projection.
- **Alternatives:** Vector DB as primary store; dual-write with no designated truth.
- **Rationale:** Correctness, governed delete, and **append-only audit** require
  transactional, queryable truth. Embeddings drift and models change; an index must be
  reconstructible without data loss.
- **Consequences:** Write-through + reconciliation complexity; but recovery is trivial
  (rebuild the index) and governance is sound. (R6 in risks.)

### ADR-02 — Explainability is a contract guarantee, not an option
- **Decision:** Every retrieval result **always** returns per-signal scores, fusion
  weights, and a trust explanation.
- **Alternatives:** Explanation as a separate endpoint / opt-in / computed on demand.
- **Rationale:** "Why did this surface and should I trust it?" must never require a second
  query or a different code path. It's the product.
- **Consequences:** Slightly larger payloads and stricter response typing; in exchange,
  clients render explainability unconditionally and the contract is stable.

### ADR-03 — Trust is decomposable (provenance × confidence × freshness), never a black box
- **Decision:** Compute trust from three independently inspectable sub-scores with a
  human-readable explanation.
- **Alternatives:** A single opaque learned trust score.
- **Rationale:** Auditable systems can't ship an unexplainable number. Decomposition lets
  users *and* tests reason about each factor.
- **Consequences:** More surface to maintain; enables the calibration harness and the UI
  trust explorer.

### ADR-04 — Hermetic, offline default path
- **Decision:** Defaults require no network, GPU, or external service: SQLite,
  brute-force vectors, in-process BM25, `HashingEmbedder`, lexical trust.
- **Alternatives:** Real embeddings / Qdrant / Postgres as defaults.
- **Rationale:** A clone must run and pass CI in one command. Determinism makes tests
  meaningful. Onboarding friction kills OSS adoption.
- **Consequences:** Default quality is a stand-in; *real* quality is opt-in — documented
  explicitly so no one mistakes the demo for the ceiling.

### ADR-05 — Scale paths live behind seams, selected by env vars, without changing the API
- **Decision:** Embedding, keyword, vector, and trust-relation backends are swappable via
  `SCP_EMBEDDER`, `SCP_KEYWORD_BACKEND`, vector-backend config, `SCP_TRUST_NLI`.
- **Alternatives:** Hard-coded production stack; fork-per-deployment.
- **Rationale:** One codebase serves laptop → cluster; the contract is the stable surface,
  the implementation varies.
- **Consequences:** Seam discipline (interfaces, factories) and gated tests; large payoff
  in portability and testability.

### ADR-06 — A model swap must pass a calibration gate (Brier/ECE) before shipping
- **Decision:** Swapping lexical trust detection for an NLI cross-encoder is gated on
  `evals/run_trust_calibration.py` measurably lowering ECE.
- **Alternatives:** Adopt NLI because it's "smarter"; ship on vibes.
- **Rationale:** A more sophisticated model that is *worse calibrated* makes trust *less*
  trustworthy. Calibration, not sophistication, is the bar.
- **Consequences:** NLI stays opt-in until it earns its place; the gate is reusable for any
  future detector. (R3 in risks.)

### ADR-07 — Weighted fusion is the default; RRF is a benchmarked knob
- **Decision:** Default retrieval fusion is weighted (keyword .3 / vector .3 / metadata .1
  / importance .1 / **trust .2**); RRF is selectable.
- **Alternatives:** RRF default; learned-to-rank.
- **Rationale:** On the eval set, weighted beat RRF (nDCG 1.00 vs 0.69) and lets trust enter
  ranking as a tunable dimension. Decisions follow the benchmark, not fashion.
- **Consequences:** Weights are a tuning surface; the eval harness justifies the default and
  guards regressions.

### ADR-08 — Namespacing + append-only audit + governed (soft) delete are mandatory
- **Decision:** Every memory is namespace-scoped; every mutation emits an immutable audit
  event; delete is soft by default (hard delete retains audit).
- **Alternatives:** Global scope; mutable history; hard delete only.
- **Rationale:** Multi-tenant safety, compliance, and "what did the agent know and when"
  are table stakes for memory touching real users.
- **Consequences:** Slight write overhead; a complete, tamper-evident history and clean
  tenant isolation. (R7 in risks.)

### ADR-09 — Reuse the SDK as the only client (DRY contract)
- **Decision:** The admin console and examples consume the published SDK; the Android app
  mirrors the same §29 contract. The engine is never special-cased for a client.
- **Alternatives:** Bespoke fetch logic per client; engine-side view models.
- **Rationale:** Every client exercises the same contract a third party would — the SDK is
  dogfooded, drift is caught early.
- **Consequences:** SDK must stay complete and versioned; clients gain correctness for free.

### ADR-10 — Strict modularity: every source file < 300 lines
- **Decision:** Hard cap of 300 lines/file across engine, SDKs, console, and app.
- **Alternatives:** Pragmatic "big file when convenient."
- **Rationale:** Small files force single responsibility, keep diffs reviewable, and make
  the codebase legible to newcomers — a precondition for OSS contribution.
- **Consequences:** More files and deliberate decomposition; sustained readability and
  testability. (Largest engine file 192 lines; console 233; Android 151.)

---

### How to use these in an interview
Pick **ADR-03, ADR-06, or ADR-01** for "tell me about a hard technical decision." Each has a
real tradeoff, a rejected alternative, and a consequence you owned — the exact shape a
Principal interview probes for. See [`09-principal-engineer-case-study.md`](09-principal-engineer-case-study.md).
