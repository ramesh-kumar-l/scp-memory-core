"""Unit tests for pure importance scoring (intelligence.scoring)."""

from scp_memory.intelligence.scoring import (
    ScoringConfig,
    explicit_score,
    frequency_score,
    recency_score,
    score_importance,
)

DAY = 86400.0


def test_recency_is_one_at_zero_and_half_at_half_life():
    assert recency_score(0, 30) == 1.0
    assert abs(recency_score(30 * DAY, 30) - 0.5) < 1e-9


def test_recency_monotonically_decreases():
    assert recency_score(DAY, 30) > recency_score(10 * DAY, 30)


def test_frequency_zero_at_no_access_and_saturates():
    assert frequency_score(0, 10) == 0.0
    assert 0.0 < frequency_score(5, 10) < frequency_score(50, 10) < 1.0


def test_explicit_pinned_and_hint_and_garbage():
    assert explicit_score({"pinned": True}) == 1.0
    assert explicit_score({"importance_hint": 0.7}) == 0.7
    assert explicit_score({"importance_hint": 5}) == 1.0  # clamped
    assert explicit_score({"importance_hint": "nope"}) == 0.0
    assert explicit_score({}) == 0.0


def test_score_importance_stays_in_unit_interval():
    cfg = ScoringConfig()
    high = score_importance(age_seconds=0, access_count=100, explicit=1.0, config=cfg)
    low = score_importance(age_seconds=3650 * DAY, access_count=0, explicit=0.0, config=cfg)
    assert 0.0 <= low < high <= 1.0
    assert high == 1.0  # fresh, frequently used, pinned


def test_new_unpinned_memory_scores_recency_weight():
    cfg = ScoringConfig()
    score = score_importance(age_seconds=0, access_count=0, explicit=0.0, config=cfg)
    assert abs(score - cfg.w_recency) < 1e-9
