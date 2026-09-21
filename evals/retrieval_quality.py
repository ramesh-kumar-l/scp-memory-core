"""Ranking-quality metrics — pure (14-ranking-model).

Used to compare fusion strategies (weighted-linear vs reciprocal-rank fusion) on a
fixed, labelled retrieval set. Graded relevance is supported but binary labels
(relevant ids) are the common case.

- ``precision_at_k`` — fraction of the top-k that are relevant.
- ``mrr`` — mean reciprocal rank of the first relevant hit.
- ``ndcg_at_k`` — rank-discounted gain normalised by the ideal ordering.
"""

import math


def precision_at_k(ranked_ids: list[str], relevant: set[str], k: int) -> float:
    """Fraction of the top-k results that are relevant."""
    if k <= 0:
        return 0.0
    top = ranked_ids[:k]
    if not top:
        return 0.0
    return sum(1 for i in top if i in relevant) / len(top)


def reciprocal_rank(ranked_ids: list[str], relevant: set[str]) -> float:
    """1/rank of the first relevant result (0 if none present)."""
    for rank, _id in enumerate(ranked_ids, start=1):
        if _id in relevant:
            return 1.0 / rank
    return 0.0


def mrr(rankings: list[tuple[list[str], set[str]]]) -> float:
    """Mean reciprocal rank over (ranked_ids, relevant) pairs."""
    if not rankings:
        return 0.0
    return sum(reciprocal_rank(r, rel) for r, rel in rankings) / len(rankings)


def _dcg(gains: list[float]) -> float:
    return sum(g / math.log2(rank + 1) for rank, g in enumerate(gains, start=1))


def ndcg_at_k(
    ranked_ids: list[str],
    relevant: set[str],
    k: int,
    *,
    grades: dict[str, float] | None = None,
) -> float:
    """Normalised discounted cumulative gain over the top-k ([0,1]).

    ``grades`` gives graded relevance per id; absent, membership in ``relevant``
    is a gain of 1. The ideal DCG sorts all available gains descending.
    """

    def gain(_id: str) -> float:
        if grades is not None:
            return grades.get(_id, 0.0)
        return 1.0 if _id in relevant else 0.0

    dcg = _dcg([gain(i) for i in ranked_ids[:k]])
    ideal_gains = sorted(
        (grades.values() if grades is not None else [1.0] * len(relevant)), reverse=True
    )
    idcg = _dcg(list(ideal_gains)[:k])
    return dcg / idcg if idcg > 0 else 0.0
