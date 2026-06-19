"""Unit tests for the pure embedding logic."""

import pytest

from scp_memory.retrieval.embedding import HashingEmbedder, cosine_similarity


def test_embed_is_deterministic_and_correct_dim():
    emb = HashingEmbedder(dim=64)
    v1 = emb.embed("user prefers dark mode")
    v2 = emb.embed("user prefers dark mode")
    assert v1 == v2
    assert len(v1) == 64


def test_identical_text_has_cosine_one():
    emb = HashingEmbedder(dim=128)
    v = emb.embed("the timezone is IST")
    assert cosine_similarity(v, v) == pytest.approx(1.0)


def test_related_text_scores_above_unrelated():
    emb = HashingEmbedder(dim=256)
    base = emb.embed("user upgraded their subscription plan")
    related = emb.embed("the user upgraded the plan")
    unrelated = emb.embed("weather forecast tomorrow rain")
    assert cosine_similarity(base, related) > cosine_similarity(base, unrelated)


def test_token_free_text_yields_zero_vector():
    emb = HashingEmbedder(dim=32)
    v = emb.embed("!!! ???")
    assert v == [0.0] * 32
    # cosine with a real vector is 0 (no overlap), and stays in range.
    assert cosine_similarity(v, emb.embed("hello")) == 0.0


def test_invalid_dim_rejected():
    with pytest.raises(ValueError):
        HashingEmbedder(dim=0)
