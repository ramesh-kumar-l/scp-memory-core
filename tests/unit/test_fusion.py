"""Unit tests for pure score fusion."""

import pytest

from scp_memory.retrieval.fusion import (
    FusionWeights,
    normalize,
    reciprocal_rank_fusion,
    weighted_fuse,
)


def test_normalize_maps_to_unit_range():
    assert normalize([1.0, 3.0, 2.0]) == [0.0, 1.0, 0.5]


def test_normalize_constant_input_is_zero():
    assert normalize([5.0, 5.0]) == [0.0, 0.0]
    assert normalize([]) == []


def test_weighted_fuse_orders_by_combined_signal():
    keyword = [10.0, 0.0]  # normalizes to [1, 0]
    vector = [0.0, 1.0]  # already [0, 1]
    importance = [0.1, 0.9]
    weights = FusionWeights(keyword=0.5, vector=0.3, importance=0.2)
    fused = weighted_fuse(keyword, vector, importance, weights)

    # Item 1: 0.5*1 + 0.3*0 + 0.2*0.1 = 0.52 ; Item 2: 0.3*1 + 0.2*0.9 = 0.48
    assert fused[0][0] > fused[1][0]
    assert fused[0][1] == {"keyword": 1.0, "vector": 0.0, "importance": 0.1}


def test_weighted_fuse_score_in_unit_range():
    fused = weighted_fuse([1.0, 2.0], [0.3, 0.6], [0.2, 0.4], FusionWeights())
    for score, _ in fused:
        assert 0.0 <= score <= 1.0


def test_rrf_rewards_top_ranks_across_lists():
    scores = reciprocal_rank_fusion([["b", "a", "c"], ["b", "a"]], k=60)
    assert scores["b"] == pytest.approx(1 / 61 + 1 / 61)
    assert scores["a"] == pytest.approx(1 / 62 + 1 / 62)
    assert scores["b"] > scores["a"] > scores["c"]
