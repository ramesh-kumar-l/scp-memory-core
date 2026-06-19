"""Freshness scoring — pure (15-trust-model).

Type-aware exponential decay of age. Same decay shape as importance recency
(``intelligence.scoring``) but parameterized by a per-type half-life chosen by the
service: a preference stays fresh far longer than an event. Freshness only
down-weights — it never deletes.
"""


def freshness_score(age_seconds: float, half_life_days: float) -> float:
    """1.0 at age 0, 0.5 after one half-life, asymptoting to 0."""
    if age_seconds <= 0:
        return 1.0
    half_life_seconds = max(half_life_days, 1e-9) * 86400.0
    return 0.5 ** (age_seconds / half_life_seconds)
