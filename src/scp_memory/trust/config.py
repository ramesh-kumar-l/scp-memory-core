"""Trust configuration — tunable, pure (15-trust-model).

Algorithmic knobs for the trust layer live next to the pure logic they
parameterize (mirrors ``retrieval.config``). Operational settings stay in
``scp_memory.config.Settings``.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field

# Type-aware freshness half-lives (days): a preference ages far slower than an
# event. Stale memories are down-weighted, never deleted (15-trust-model).
_HALF_LIFE_DAYS: dict[str, float] = {
    "preference": 180.0,
    "fact": 90.0,
    "summary": 120.0,
    "event": 14.0,
    "other": 60.0,
}
_DEFAULT_HALF_LIFE_DAYS = 60.0


@dataclass(frozen=True)
class TrustWeights:
    """Composite-trust weights. Need not sum to 1; aggregation normalizes by sum."""

    provenance: float = 0.4
    confidence: float = 0.4
    freshness: float = 0.2


@dataclass(frozen=True)
class TrustConfig:
    weights: TrustWeights = field(default_factory=TrustWeights)
    half_life_days: Mapping[str, float] = field(default_factory=lambda: dict(_HALF_LIFE_DAYS))
    default_half_life_days: float = _DEFAULT_HALF_LIFE_DAYS
    # Lexical overlap (Jaccard) at/above which a same-type neighbour is "about the
    # same thing" — then agreeing polarity corroborates, divergent polarity
    # contradicts. Kept moderate: real contradictions ("wants X" vs "does not want
    # X") carry extra negation tokens that depress overlap.
    corroboration_threshold: float = 0.5
    # Corroborating-neighbour count at which the confidence boost ≈ 0.63 saturates.
    corroboration_saturation: float = 3.0
    # Confidence subtracted per contradicting (negation-divergent) neighbour.
    contradiction_penalty: float = 0.25
    # Cap on neighbours scanned for corroboration in the standalone explain path.
    neighbor_limit: int = 500

    def half_life_for(self, type_: str) -> float:
        """Freshness half-life (days) for a memory type, falling back to the default."""
        return self.half_life_days.get(type_, self.default_half_life_days)
