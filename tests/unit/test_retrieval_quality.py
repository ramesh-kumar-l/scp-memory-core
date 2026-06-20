"""Unit tests for ranking-quality metrics and the fusion benchmark harness."""

from evals.loader import load_dataset
from evals.retrieval_quality import (
    mrr,
    ndcg_at_k,
    precision_at_k,
    reciprocal_rank,
)
from evals.run_retrieval_benchmark import report


def test_precision_at_k():
    assert precision_at_k(["a", "b", "c"], {"a", "c"}, 3) == 2 / 3
    assert precision_at_k([], {"a"}, 3) == 0.0
    assert precision_at_k(["a"], {"a"}, 0) == 0.0


def test_reciprocal_rank_first_hit():
    assert reciprocal_rank(["x", "y", "a"], {"a"}) == 1 / 3
    assert reciprocal_rank(["a", "b"], {"a"}) == 1.0
    assert reciprocal_rank(["x", "y"], {"a"}) == 0.0


def test_mrr_averages_queries():
    rankings = [(["a", "b"], {"a"}), (["x", "y", "z"], {"z"})]
    assert mrr(rankings) == (1.0 + 1 / 3) / 2


def test_ndcg_perfect_ordering_is_one():
    assert ndcg_at_k(["a", "b", "c"], {"a", "b"}, 3) == 1.0


def test_ndcg_rewards_higher_ranked_relevance():
    good = ndcg_at_k(["a", "x", "y"], {"a"}, 3)
    worse = ndcg_at_k(["x", "y", "a"], {"a"}, 3)
    assert good > worse


def test_ndcg_supports_graded_relevance():
    grades = {"a": 3.0, "b": 1.0}
    perfect = ndcg_at_k(["a", "b"], set(), 2, grades=grades)
    flipped = ndcg_at_k(["b", "a"], set(), 2, grades=grades)
    assert perfect == 1.0
    assert flipped < perfect


def test_benchmark_harness_runs_both_methods():
    data = load_dataset("retrieval_eval.json")
    results = report(data)
    assert set(results) == {"weighted", "rrf"}
    for metrics in results.values():
        assert 0.0 <= metrics["ndcg"] <= 1.0
        assert 0.0 <= metrics["mrr"] <= 1.0
