# Phase 4 — Trust Layer

**Status:** Implemented (v0.4.0). Trustworthy, explainable recall: every retrieved
memory carries a decomposable trust verdict, and trust enters ranking as an
additional weighted dimension.

See the design intent in [`15-trust-model`](../project-memory-bank/15-trust-model.md)
and [`14-ranking-model`](../project-memory-bank/14-ranking-model.md).

## What's implemented

Four trust signals, computed per memory:

| Signal | Meaning | Source of truth |
|---|---|---|
| **provenance_quality** | How the memory was obtained (user-stated > inferred > system) | `Provenance.source` |
| **confidence** | Certainty it's correct: provenance floor, raised by corroboration, lowered by contradiction | neighbours in the candidate set |
| **freshness** | Type-aware recency (a `preference` ages far slower than an `event`) | `created_at` + per-type half-life |
| **score** | Weighted composite of the three (the dimension fed to ranking) | `TrustWeights` |

Each result also carries a one-sentence **explanation** assembled from those same
numbers — no black boxes.

## Explainability contract

A hybrid search result now looks like:

```json
{
  "score": 0.95,
  "signals": { "keyword": 1.0, "vector": 1.0, "metadata": 1.0,
               "importance": 0.5, "trust": 1.0 },
  "weights": { "keyword": 0.35, "vector": 0.35, "importance": 0.1, "trust": 0.2 },
  "trust": {
    "provenance_quality": 1.0, "confidence": 1.0, "freshness": 1.0,
    "score": 1.0,
    "explanation": "user-stated (high provenance); corroborated by 1 memory;
                    recorded today. Confidence 1.00, fresh (freshness 1.00)."
  }
}
```

`trust` appears both as a fused **signal** (in `signals`/`weights`, so you can see
its weight in the rank) and as a full **breakdown** (so you can see why).

## Honest stand-in (same pattern as the Phase-3 embedder)

Corroboration and contradiction are detected **lexically**, not semantically:

- **Corroboration** — a same-type neighbour whose token overlap (Jaccard) clears
  `corroboration_threshold` (0.5) and shares the same negation polarity.
- **Contradiction** — a similar neighbour whose negation polarity *diverges*
  (one says "wants X", the other "does **not** want X").

This is deliberate and documented: it's hermetic, zero-infra, and reproducible —
and it swaps for real NLI/semantic entailment behind the same `trust_service`
contract, exactly as `HashingEmbedder` swaps for a real embedding model. It will
miss paraphrased agreement and subtle contradictions.

## API

- `POST /v1/retrieval/search` — results now carry `signals.trust`, `weights.trust`,
  and the `trust` breakdown. New optional body field `min_confidence` (0–1) drops
  results below that trust confidence (filtered, never silently hidden elsewhere).
- `GET /v1/trust/{memory_id}?namespace=...` — standalone explainability: the trust
  breakdown for one memory, evaluated against its active same-type neighbours.
  `404` if the memory isn't in that namespace.

## Configuration

Algorithmic knobs live next to the pure logic in
[`trust/config.py`](../src/scp_memory/trust/config.py): per-type freshness
half-lives, corroboration threshold/saturation, contradiction penalty, and the
composite `TrustWeights`. Ranking weights (incl. the trust weight) live in
[`retrieval/config.py`](../src/scp_memory/retrieval/config.py).

## Layout (strict modularity — all files < 300 lines)

```
src/scp_memory/trust/            # pure, I/O-free
  provenance.py  freshness.py  confidence.py  score.py  explain.py  config.py
src/scp_memory/services/trust_service.py   # DB-aware orchestration (no writes)
src/scp_memory/api/routes/trust.py         # explain endpoint
```

`trust_service.evaluate_all()` pre-tokenizes the candidate set once (O(N)
tokenizations, O(N²) comparisons over the bounded candidate window); provenance is
eager-loaded in the retrieval candidate query to avoid N+1.

## Run

```bash
python examples/trust_quickstart.py     # in-process demo (no server/DB setup)
pytest -q                               # 86 tests
```

## Not in Phase 4 (deferred)

- Semantic corroboration/contradiction (NLI) behind the same seam.
- Trust **calibration** measurement (predicted confidence vs. observed
  correctness) — needs a fixed eval set; tracked in
  [`21-benchmark-results`](../project-memory-bank/21-benchmark-results.md).
- Provenance graph quality (multi-hop derivation scoring) beyond the direct source.
