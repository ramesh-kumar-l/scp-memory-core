"""Unit tests for pure BM25 keyword scoring."""

from scp_memory.intelligence.similarity import tokenize
from scp_memory.retrieval.keyword import bm25_scores


def _docs(*texts):
    return [list(tokenize(t)) for t in texts]


def test_empty_query_or_corpus_scores_zero():
    assert bm25_scores([], _docs("anything")) == [0.0]
    assert bm25_scores(["x"], []) == []


def test_document_with_query_term_ranks_highest():
    docs = _docs(
        "user prefers dark mode in the app",
        "user lives in the mountain timezone",
        "completely unrelated content here",
    )
    scores = bm25_scores(list(tokenize("dark mode")), docs)
    assert scores[0] == max(scores)
    assert scores[0] > 0.0


def test_rare_term_outweighs_common_term():
    # "the" appears everywhere (low idf); "qdrant" is rare (high idf).
    docs = _docs("the the the the", "qdrant the", "the the")
    scores = bm25_scores(list(tokenize("qdrant the")), docs)
    assert scores[1] == max(scores)
