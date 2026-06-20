"""Embedder selection (ADR-011): default hashing, opt-in local model."""

import pytest

from scp_memory.config import Settings
from scp_memory.retrieval.embedder_factory import build_embedder
from scp_memory.retrieval.embedding import HashingEmbedder


def test_default_is_hashing_stand_in():
    embedder = build_embedder(Settings(embedder="hashing"))
    assert isinstance(embedder, HashingEmbedder)


def test_unknown_choice_falls_back_to_hashing():
    embedder = build_embedder(Settings(embedder="nonsense"))
    assert isinstance(embedder, HashingEmbedder)


def test_hashing_embedder_is_deterministic_unit_vector():
    embedder = build_embedder(Settings(embedder="hashing"))
    a, b = embedder.embed("dark mode preference"), embedder.embed("dark mode preference")
    assert a == b
    assert abs(sum(x * x for x in a) - 1.0) < 1e-9  # L2-normalized


def test_sentence_transformers_selection_builds_local_model():
    """Opt-in local embedder. Skips cleanly if the lib or model cache is absent."""
    pytest.importorskip("sentence_transformers")
    from scp_memory.retrieval.local_embedder import SentenceTransformerEmbedder

    try:
        embedder = build_embedder(Settings(embedder="sentence-transformers"))
    except Exception as exc:  # offline + no cached model → not a unit-test failure
        pytest.skip(f"local model unavailable offline: {exc}")
    assert isinstance(embedder, SentenceTransformerEmbedder)
    vec = embedder.embed("the user prefers dark mode")
    assert len(vec) == embedder.dim
    assert abs(sum(x * x for x in vec) - 1.0) < 1e-3  # normalized embeddings
