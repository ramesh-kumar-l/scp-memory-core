"""Unit tests for the calibration metrics and the trust-calibration harness."""

import pytest
from evals.calibration import (
    brier_score,
    expected_calibration_error,
    reliability_table,
)
from evals.loader import load_dataset
from evals.run_trust_calibration import score_dataset


def test_brier_perfect_and_worst():
    assert brier_score([1.0, 0.0], [1, 0]) == 0.0
    assert brier_score([0.0, 1.0], [1, 0]) == 1.0


def test_brier_length_mismatch_raises():
    with pytest.raises(ValueError):
        brier_score([0.5], [1, 0])


def test_ece_zero_for_perfectly_calibrated():
    # Within each bin, predicted confidence equals observed accuracy exactly.
    probs = [0.0, 0.0, 1.0, 1.0]
    outcomes = [0, 0, 1, 1]
    assert expected_calibration_error(probs, outcomes, bins=10) == 0.0


def test_ece_positive_when_overconfident():
    # All predicted 0.9 but only half correct -> gap of 0.4.
    probs = [0.9, 0.9, 0.9, 0.9]
    outcomes = [1, 1, 0, 0]
    assert expected_calibration_error(probs, outcomes, bins=10) == pytest.approx(0.4)


def test_reliability_table_only_nonempty_bins():
    table = reliability_table([0.05, 0.95], [0, 1], bins=10)
    assert len(table) == 2
    assert table[0].count == 1 and table[-1].avg_accuracy == 1.0


def test_confidence_1_lands_in_last_bin():
    table = reliability_table([1.0], [1], bins=10)
    assert len(table) == 1
    assert table[0].avg_confidence == 1.0


def test_harness_runs_on_fixed_dataset_and_is_bounded():
    items = load_dataset("trust_eval.json")["items"]
    probs, outcomes = score_dataset(items)
    assert len(probs) == len(outcomes) == len(items)
    assert all(0.0 <= p <= 1.0 for p in probs)
    ece = expected_calibration_error(probs, outcomes, bins=5)
    brier = brier_score(probs, outcomes)
    assert 0.0 <= ece <= 1.0
    assert 0.0 <= brier <= 1.0
