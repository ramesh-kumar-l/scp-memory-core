"""Score fusion & normalization — pure (14-ranking-model).

Candidate generators produce heterogeneous scores (BM25 is unbounded; cosine is
[0,1]; importance is [0,1]). Fusion reconciles them into a single ordering. Two
methods, per the ranking model:

- ``weighted_fuse`` — min-max normalize each relevance signal across the candidate
  set, then a weighted linear combination. Interpretable: the per-signal
  contributions are exactly the explainability payload.
- ``reciprocal_rank_fusion`` — rank-based, robust to scale differences.

Phase 3 defaults to weighted fusion (explainable); RRF is selectable per query.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class FusionWeights:
    """Relevance/quality weights. Need not sum to 1; fusion normalizes by their sum.

    ``trust`` (Phase 4) defaults to 0.0 so Phase-3 callers are unaffected; the
    retrieval default config sets it positive to weight the trust dimension.
    """

    keyword: float = 0.4
    vector: float = 0.4
    importance: float = 0.2
    trust: float = 0.0


def normalize(values: list[float]) -> list[float]:
    """Min-max normalize to [0, 1]; constant inputs map to 0.0 (no discriminative signal)."""
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi <= lo:
        return [0.0] * len(values)
    span = hi - lo
    return [(v - lo) / span for v in values]


def weighted_fuse(
    keyword: list[float],
    vector: list[float],
    importance: list[float],
    weights: FusionWeights,
    trust: list[float] | None = None,
) -> list[tuple[float, dict[str, float]]]:
    """Fuse signals into (score, per-signal-contribution) pairs, aligned with inputs.

    ``keyword`` and ``vector`` are normalized across the candidate set so their
    scales are comparable; ``importance`` and ``trust`` are already in [0, 1] and
    used as-is. ``trust`` (Phase 4) is optional: when omitted, the result and its
    contribution dict are identical to Phase 3 (no ``trust`` key).
    """
    kw = normalize(keyword)
    vec = normalize(vector)
    use_trust = trust is not None
    tr = trust if use_trust else [0.0] * len(keyword)
    tw = weights.trust if use_trust else 0.0
    total = (weights.keyword + weights.vector + weights.importance + tw) or 1.0

    fused: list[tuple[float, dict[str, float]]] = []
    for i in range(len(keyword)):
        score = (
            weights.keyword * kw[i]
            + weights.vector * vec[i]
            + weights.importance * importance[i]
            + tw * tr[i]
        ) / total
        parts = {
            "keyword": round(kw[i], 4),
            "vector": round(vec[i], 4),
            "importance": round(importance[i], 4),
        }
        if use_trust:
            parts["trust"] = round(tr[i], 4)
        fused.append((score, parts))
    return fused


def reciprocal_rank_fusion(rank_lists: list[list[str]], k: int = 60) -> dict[str, float]:
    """Combine ranked id-lists into ``{id: rrf_score}`` (robust to scale differences)."""
    scores: dict[str, float] = {}
    for ranked in rank_lists:
        for rank, item_id in enumerate(ranked):
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank + 1)
    return scores
