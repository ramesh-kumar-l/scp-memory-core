"""Human-readable trust explanations — pure (15-trust-model).

No black boxes: every retrieved memory can state, in plain language, why it is (or
isn't) trusted — assembled from the same numbers that drive ranking.
"""


def _provenance_phrase(source: str | None, quality: float) -> str:
    label = source or "unknown"
    if quality >= 0.9:
        return f"{label}-stated (high provenance)"
    if quality >= 0.6:
        return f"derived from {label} (moderate provenance)"
    return f"{label} source (low provenance)"


def _age_phrase(age_days: float) -> str:
    days = int(round(age_days))
    if days <= 0:
        return "recorded today"
    if days == 1:
        return "last updated 1 day ago"
    return f"last updated {days} days ago"


def explain(
    *,
    source: str | None,
    provenance_quality: float,
    confidence: float,
    freshness: float,
    corroboration: int,
    contradiction: int,
    age_days: float,
) -> str:
    """Compose a one-sentence trust rationale from its inputs."""
    parts = [_provenance_phrase(source, provenance_quality)]
    if corroboration > 0:
        noun = "memory" if corroboration == 1 else "memories"
        parts.append(f"corroborated by {corroboration} {noun}")
    if contradiction > 0:
        noun = "memory" if contradiction == 1 else "memories"
        parts.append(f"contradicted by {contradiction} {noun}")
    parts.append(_age_phrase(age_days))
    fresh_word = "fresh" if freshness >= 0.5 else "stale"
    return (
        f"{'; '.join(parts)}. Confidence {confidence:.2f}, "
        f"{fresh_word} (freshness {freshness:.2f})."
    )
