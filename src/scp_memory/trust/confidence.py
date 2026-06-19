"""Confidence scoring — pure (15-trust-model).

Confidence is how certain we are a memory is correct. It starts from provenance
quality, rises with corroboration (independent memories that agree), and falls
with contradiction. The corroboration/contradiction *counts* are produced by the
service against the candidate set; this module only combines them.
"""

import math


def corroboration_boost(count: int, saturation: float) -> float:
    """0 with no support, rising and saturating toward 1 as agreeing memories add up."""
    if count <= 0:
        return 0.0
    return 1.0 - math.exp(-count / max(saturation, 1e-9))


def confidence_score(
    *,
    provenance_quality: float,
    corroboration: int,
    contradiction: int,
    saturation: float,
    contradiction_penalty: float,
) -> float:
    """Combine provenance, corroboration and contradiction into [0, 1].

    Corroboration closes the gap between the provenance floor and 1.0; each
    contradiction subtracts a fixed penalty. Clamped to stay a valid signal.
    """
    base = min(1.0, max(0.0, provenance_quality))
    boost = (1.0 - base) * corroboration_boost(corroboration, saturation)
    penalty = max(0, contradiction) * contradiction_penalty
    return round(min(1.0, max(0.0, base + boost - penalty)), 4)
