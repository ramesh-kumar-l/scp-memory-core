# 12 — Talk / Presentation Deck

> **Artifact 9 of the 80/20 set.** Unlocks conference CFPs and meetups — high-bandwidth
> visibility and a durable authority signal. This is the deck outline + abstract; build the
> slides from it.

---

## Talk title

**"Memory Your Agent — and Your Auditor — Can Trust: Building an Explainable Memory Layer for AI Agents"**

Alt: *"Beyond the Vector Index: Trust-Aware Memory Infrastructure for Long-Lived Agents."*

## Abstract (CFP-ready, ~120 words)

> As AI moves from stateless prompts to long-lived agents, "memory" has quietly become the
> hardest unsolved infrastructure problem — and bolting on a vector database doesn't solve
> it. A vector store can't tell a user-confirmed fact from a model's stale guess, can't
> explain why a memory surfaced, and has no audit trail. This talk walks through the design
> of an open-source **trust-aware, explainable memory layer**: how to make trust a
> decomposable ranking signal (provenance × confidence × freshness), why explainability has
> to be a contract guarantee, and a calibration discipline that blocks "smarter" models that
> are actually worse. You'll leave with a reusable architecture for memory-as-infrastructure
> and a running demo you can clone tonight.

## Audience

Primary: backend/infra and ML-platform engineers building agents. Secondary: eng leaders
evaluating memory/RAG approaches. Level: intermediate–advanced. Venues: AI infra meetups,
PyCon/PyData, platform-engineering conferences, internal tech talks.

## Outline (30–40 min)

1. **Hook (3 min)** — A long-lived agent confidently acts on a memory the user *retracted
   yesterday*. Why? Because the store had no notion of trust. (Live: contradiction demo.)
2. **The category argument (5 min)** — Stateless → long-lived agents; the 3 failures of
   vector-as-memory (no trust, no explanation, no governance). Memory is *infrastructure*.
3. **Trust as a first-class signal (8 min)** — Decomposition: provenance × confidence ×
   freshness. The diagram. Why decomposable beats a learned black box.
4. **Explainable hybrid retrieval (7 min)** — keyword ∪ vector ∪ metadata → fuse → rank →
   attach trust; per-signal scores as a *contract*. Live: the console's score bars.
5. **Calibrate before you sophisticate (6 min)** — The Brier/ECE gate; the war story of the
   NLI detector that had to *earn* its place. The Principal-level idea of the talk.
6. **Hermetic by default, pluggable at scale (4 min)** — Seams: one codebase laptop→cluster.
7. **Governance (3 min)** — Namespacing, append-only audit, right-to-be-forgotten.
8. **Close + CTA (2 min)** — Repo, the 10 golden examples, the blog series. ⭐.

## Key slides (the ones that carry the talk)

- **S1 Title** — tagline + a single screenshot of trust score bars.
- **S2 "The retracted memory"** — the failure that motivates everything.
- **S3 The gap table** — vector DB vs agent-memory libs vs SCP (from [`00`](00-project-analysis.md)).
- **S4 Trust decomposition** — the provenance→confidence→freshness tree (mermaid).
- **S5 Retrieval pipeline** — the sequence diagram (from [`05`](05-architecture-document.md)).
- **S6 A real response** — JSON with `signals` + `weights` + `trust.explanation` highlighted.
- **S7 Calibration gate** — Brier/ECE before/after; "we said no to the smarter model."
- **S8 Seams** — the backends diagram; env-var swap, contract unchanged.
- **S9 Demo** — live contradiction query; light-mode beats dark-mode, explained.
- **S10 CTA** — repo + blog series + "clone it tonight."

## Demo script (the live moment)

```bash
python -m scp_memory & ; python seed/seed_golden_examples.py
# ask: "what theme does the user like?"  → light-mode ranks first, with the
# trust explanation: "user-stated, recent, contradicts an earlier preference"
```
Have a recorded fallback GIF in case the live demo fails.

## Reuse

- Abstract ← [`04-engineering-thesis.md`](04-engineering-thesis.md)
- Slides 4–8 ← [`05`](05-architecture-document.md) + [`06`](06-adr-collection.md) + [`08`](08-benchmark-report.md)
- Demo ← [`11-demo-and-examples-pack.md`](11-demo-and-examples-pack.md)
- A recorded version of this talk doubles as the README hero video.
