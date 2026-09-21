"""Importance scoring — pure functions (12-memory-model, 14-ranking-model).

`importance` in [0, 1] fuses three normalized signals:

- **recency**   — exponential decay of age (half-life configurable).
- **frequency** — saturating function of access count.
- **explicit**  — caller-provided hint (`pinned` / `importance_hint` in metadata).

Weights sum to 1.0, so the fused score stays in [0, 1] without extra clamping.
The service layer ([importance_service]) feeds DB values in; this module never
touches the database.
"""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class ScoringConfig:
    """Tunable weights/parameters for importance scoring.

    Defaults are empirical Phase-2 starting points; recorded in
    21-benchmark-results and refined as real usage data arrives.
    """

    w_recency: float = 0.5
    w_frequency: float = 0.3
    w_explicit: float = 0.2
    half_life_days: float = 30.0
    freq_saturation: float = 10.0  # access count at which frequency ≈ 0.63


def recency_score(age_seconds: float, half_life_days: float) -> float:
    """1.0 at age 0, 0.5 after one half-life, asymptoting to 0."""
    if age_seconds <= 0:
        return 1.0
    half_life_seconds = max(half_life_days, 1e-9) * 86400.0
    return 0.5 ** (age_seconds / half_life_seconds)


def frequency_score(access_count: int, saturation: float) -> float:
    """0.0 at no accesses, rising and saturating toward 1.0."""
    if access_count <= 0:
        return 0.0
    return 1.0 - math.exp(-access_count / max(saturation, 1e-9))


def explicit_score(meta: dict | None) -> float:
    """Caller-supplied importance signal from metadata.

    `pinned` (truthy) forces the maximum; otherwise `importance_hint` is read as a
    float and clamped to [0, 1]. Unknown/invalid values contribute nothing.
    """
    if not meta:
        return 0.0
    if meta.get("pinned"):
        return 1.0
    hint = meta.get("importance_hint")
    if hint is None:
        return 0.0
    try:
        value = float(hint)
    except (TypeError, ValueError):
        return 0.0
    return min(1.0, max(0.0, value))


def score_importance(
    *,
    age_seconds: float,
    access_count: int,
    explicit: float,
    config: ScoringConfig,
) -> float:
    """Fuse the three signals into a single importance value in [0, 1]."""
    fused = (
        config.w_recency * recency_score(age_seconds, config.half_life_days)
        + config.w_frequency * frequency_score(access_count, config.freq_saturation)
        + config.w_explicit * min(1.0, max(0.0, explicit))
    )
    return round(min(1.0, max(0.0, fused)), 4)
