"""Calibration metrics — pure (24-known-risks R3).

A trust *confidence* of 0.8 should mean "right about 80% of the time". These
metrics quantify the gap between predicted confidence and observed correctness so
the lexical→NLI decision is driven by measurement, not assumption.

- ``brier_score`` — mean squared error of probabilistic predictions (lower better).
- ``reliability_table`` — per-bin predicted-vs-observed (the reliability diagram).
- ``expected_calibration_error`` — single-number summary: support-weighted mean
  gap between confidence and accuracy across bins (lower better).
"""

from dataclasses import dataclass


def brier_score(probs: list[float], outcomes: list[int]) -> float:
    """Mean squared error between predicted probabilities and {0,1} outcomes."""
    if not probs:
        return 0.0
    if len(probs) != len(outcomes):
        raise ValueError("probs and outcomes must be the same length")
    return sum((p - o) ** 2 for p, o in zip(probs, outcomes, strict=True)) / len(probs)


@dataclass(frozen=True)
class ReliabilityBin:
    lo: float
    hi: float
    count: int
    avg_confidence: float
    avg_accuracy: float


def reliability_table(
    probs: list[float], outcomes: list[int], *, bins: int = 10
) -> list[ReliabilityBin]:
    """Bucket predictions into equal-width confidence bins; report mean conf vs acc.

    Only non-empty bins are returned. The rightmost edge is inclusive so a
    confidence of exactly 1.0 lands in the last bin.
    """
    if len(probs) != len(outcomes):
        raise ValueError("probs and outcomes must be the same length")
    width = 1.0 / bins
    table: list[ReliabilityBin] = []
    for b in range(bins):
        lo, hi = b * width, (b + 1) * width
        members = [
            (p, o)
            for p, o in zip(probs, outcomes, strict=True)
            if (lo <= p < hi) or (b == bins - 1 and p == hi)
        ]
        if not members:
            continue
        n = len(members)
        table.append(
            ReliabilityBin(
                lo=lo,
                hi=hi,
                count=n,
                avg_confidence=sum(p for p, _ in members) / n,
                avg_accuracy=sum(o for _, o in members) / n,
            )
        )
    return table


def expected_calibration_error(probs: list[float], outcomes: list[int], *, bins: int = 10) -> float:
    """Support-weighted mean |confidence − accuracy| over bins ([0,1], lower better)."""
    if not probs:
        return 0.0
    total = len(probs)
    table = reliability_table(probs, outcomes, bins=bins)
    return sum(b.count / total * abs(b.avg_confidence - b.avg_accuracy) for b in table)
