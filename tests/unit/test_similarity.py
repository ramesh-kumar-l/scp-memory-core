"""Unit tests for pure text similarity (intelligence.similarity)."""

from scp_memory.intelligence.similarity import jaccard, tokenize


def test_tokenize_lowercases_and_splits_on_punctuation():
    assert tokenize("Dark-mode, please!") == {"dark", "mode", "please"}


def test_jaccard_identical_and_disjoint():
    a = tokenize("user prefers dark mode")
    b = tokenize("user prefers dark mode")
    assert jaccard(a, b) == 1.0
    assert jaccard(tokenize("apples"), tokenize("oranges")) == 0.0


def test_jaccard_partial_overlap():
    a = tokenize("user prefers dark mode")
    b = tokenize("user prefers light mode")
    # overlap {user, prefers, mode} = 3, union = 5
    assert abs(jaccard(a, b) - 3 / 5) < 1e-9


def test_jaccard_two_empty_sets_is_one():
    assert jaccard(set(), set()) == 1.0
