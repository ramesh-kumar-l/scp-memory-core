"""Composite trust aggregation — pure (14-ranking-model, 15-trust-model).

Fuses the trust signals into one [0, 1] score that enters ranking as an extra
weighted dimension. Decomposable by design: the inputs are carried alongside the
result so a consumer can reconstruct the number.
"""

from scp_memory.trust.config import TrustWeights


def trust_score(
    *,
    provenance_quality: float,
    confidence: float,
    freshness: float,
    weights: TrustWeights,
) -> float:
    """Weighted combination of the trust signals into a single [0, 1] score."""
    total = (weights.provenance + weights.confidence + weights.freshness) or 1.0
    fused = (
        weights.provenance * provenance_quality
        + weights.confidence * confidence
        + weights.freshness * freshness
    ) / total
    return round(min(1.0, max(0.0, fused)), 4)
