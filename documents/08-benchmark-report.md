# 08 — Benchmark Report

> **Artifact 5 of the 80/20 set.** Converts claims into numbers and pre-empts the skeptical
> engineer. Reports what the existing `evals/` harnesses measure; clearly separates
> **measured** results from **template/TODO** so nothing is overclaimed.

---

## Why this report exists

Two claims need proof, not adjectives:
1. **"Explainable hybrid retrieval is *good* retrieval."** — measured with ranking quality
   (nDCG, MRR) and the weighted-vs-RRF comparison.
2. **"Trust is *trustworthy*."** — measured with calibration (Brier score, ECE), because a
   trust signal that's confidently wrong is worse than none.

Plus an operational claim: **latency stays within SLO**.

## Metrics

| Metric | What it answers | Where |
|---|---|---|
| **nDCG@k** | Are relevant memories ranked near the top? | `evals/` retrieval benchmark |
| **MRR** | How high is the first relevant result? | `evals/` retrieval benchmark |
| **Weighted vs RRF** | Which fusion default is better? | `evals/` retrieval benchmark |
| **Brier score** | Are trust confidences well-calibrated? (lower better) | `evals/run_trust_calibration.py` |
| **ECE** | Expected calibration error (lower better) | `evals/run_trust_calibration.py` |
| **p50/p95/p99 latency** | Operational SLO compliance | `/metrics` histogram |

## Methodology

- **Fixed labelled datasets** checked into `evals/` — deterministic, reproducible, no
  network. Retrieval set = queries with graded relevance labels; calibration set = memories
  with ground-truth trust labels (e.g. a known contradiction pair, a corroborated fact).
- **Hermetic default stack** (SQLite + brute-force + BM25 + lexical trust) so anyone
  reproduces the numbers with `pip install -e . && python evals/...`.
- **Apples-to-apples fusion comparison:** same candidates, same labels, weighted vs RRF.
- **Calibration as a gate:** results feed ADR-06 — a detector swap ships only if ECE drops.

## Baselines

| Baseline | Role |
|---|---|
| Keyword-only (BM25) | Lower bound on retrieval; no semantics |
| Vector-only (HashingEmbedder) | Semantic-ish lower bound, hermetic |
| **Hybrid weighted (default)** | The system under test |
| Hybrid RRF | Alternative fusion |
| Lexical trust detector (default) | Calibration baseline |
| NLI cross-encoder (opt-in) | Calibration challenger (gated) |

## Results (measured to date)

> These reflect the current hermetic eval sets. They are **directional** (small fixed sets,
> stand-in embeddings), stated as such on purpose.

- **Fusion:** weighted fusion **nDCG ≈ 1.00 vs RRF ≈ 0.69** on the eval set → confirms
  weighted as the default (ADR-07).
- **Trust calibration (lexical baseline):** **Brier ≈ 0.17 / ECE ≈ 0.19**, with visible
  **over-confidence on semantic contradictions** (e.g. dark/light, berlin/munich) the
  lexical detector mis-reads. This is the documented motivation for the NLI seam — and the
  bar it must clear (lower ECE) before adoption.
- **NLI challenger:** **not yet run through the harness** (needs the `[embeddings]` model);
  adoption pending a measured ECE improvement.

## Latency (template — fill from a real run)

| Endpoint | p50 | p95 | p99 | SLO |
|---|---|---|---|---|
| `POST /v1/retrieval/search` | _TODO_ | _TODO_ | _TODO_ | p95 < 150 ms (local) |
| `POST /v1/memories` | _TODO_ | _TODO_ | _TODO_ | p95 < 50 ms |
| `GET /v1/trust/{id}` | _TODO_ | _TODO_ | _TODO_ | p95 < 50 ms |

Capture from the `/metrics` histogram (console Benchmarks screen or `curl /metrics`) under
a fixed load; record machine + dataset size alongside.

## Conclusions

1. **Weighted fusion is the right default** on current evidence — and the harness guards
   against regressions.
2. **The lexical trust detector is usable but over-confident on semantic contradictions** —
   an honest, measured limitation, with the upgrade path (NLI) defined and gated.
3. **Calibration-as-a-gate is the headline methodology contribution:** the project refuses
   to ship a "smarter" model that is worse calibrated. That discipline is the Principal-level
   signal a benchmark report should broadcast.

## Reproduce

```bash
pip install -e .
python evals/run_retrieval_benchmark.py     # nDCG / MRR, weighted vs RRF
python evals/run_trust_calibration.py        # Brier / ECE
# optional challenger:
SCP_TRUST_NLI=1 pip install -e ".[embeddings]" && python evals/run_trust_calibration.py
```

> **Integrity note:** every number here is labelled measured / directional / TODO. When the
> latency table and NLI run are filled from real runs, update this file and the README — and
> never round a directional result into a headline claim.
