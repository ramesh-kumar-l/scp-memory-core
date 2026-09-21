"""Provenance-quality scoring — pure (15-trust-model).

Quality reflects *how* a memory was obtained: user-stated outranks inferred;
consolidation inherits decent quality from its sources. Unknown sources get a
neutral default rather than a penalty — absence of evidence is not evidence of
low quality.
"""

_QUALITY: dict[str, float] = {
    "user": 1.0,
    "explicit": 1.0,
    "settings": 0.9,
    "consolidation": 0.75,
    "import": 0.7,
    "external": 0.5,
    "inferred": 0.5,
    "system": 0.4,
}
_DEFAULT_QUALITY = 0.5


def provenance_quality(source: str | None) -> float:
    """Map a provenance source to a quality score in [0, 1]."""
    if not source:
        return _DEFAULT_QUALITY
    return _QUALITY.get(source.lower(), _DEFAULT_QUALITY)
