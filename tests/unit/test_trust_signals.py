"""Unit tests for the pure trust signal scorers (Phase 4)."""

from scp_memory.trust.confidence import confidence_score, corroboration_boost
from scp_memory.trust.config import TrustWeights
from scp_memory.trust.freshness import freshness_score
from scp_memory.trust.provenance import provenance_quality
from scp_memory.trust.score import trust_score

DAY = 86400.0


def test_provenance_quality_ranks_user_above_inferred():
    assert provenance_quality("user") > provenance_quality("inferred")
    assert provenance_quality("inferred") > provenance_quality("system")


def test_provenance_quality_is_case_insensitive_with_neutral_default():
    assert provenance_quality("USER") == provenance_quality("user")
    assert provenance_quality("totally-unknown-source") == 0.5
    assert provenance_quality(None) == 0.5


def test_freshness_decays_with_age():
    assert freshness_score(0.0, 30.0) == 1.0
    assert freshness_score(30 * DAY, 30.0) == 0.5  # one half-life
    assert freshness_score(120 * DAY, 30.0) < 0.1


def test_freshness_is_type_aware_via_half_life():
    # Same age, longer half-life (preference) stays fresher than a shorter one (event).
    age = 30 * DAY
    assert freshness_score(age, 180.0) > freshness_score(age, 14.0)


def test_corroboration_boost_saturates():
    assert corroboration_boost(0, 3.0) == 0.0
    assert corroboration_boost(3, 3.0) < corroboration_boost(10, 3.0)
    assert corroboration_boost(100, 3.0) < 1.0


def test_confidence_rises_with_corroboration_falls_with_contradiction():
    base = confidence_score(
        provenance_quality=0.5,
        corroboration=0,
        contradiction=0,
        saturation=3.0,
        contradiction_penalty=0.25,
    )
    supported = confidence_score(
        provenance_quality=0.5,
        corroboration=3,
        contradiction=0,
        saturation=3.0,
        contradiction_penalty=0.25,
    )
    contradicted = confidence_score(
        provenance_quality=0.5,
        corroboration=0,
        contradiction=2,
        saturation=3.0,
        contradiction_penalty=0.25,
    )
    assert supported > base > contradicted
    assert 0.0 <= contradicted <= 1.0


def test_trust_score_is_weighted_combination_in_unit_range():
    weights = TrustWeights(provenance=0.4, confidence=0.4, freshness=0.2)
    score = trust_score(provenance_quality=1.0, confidence=0.5, freshness=0.0, weights=weights)
    # 0.4*1 + 0.4*0.5 + 0.2*0 = 0.6 (weights already sum to 1).
    assert score == 0.6
    assert 0.0 <= score <= 1.0
