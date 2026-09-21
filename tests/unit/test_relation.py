"""Unit tests for the pure pairwise relation logic and the detector seam."""

from scp_memory.intelligence.similarity import tokenize
from scp_memory.services.relation_detector import (
    LexicalRelationDetector,
    get_relation_detector,
)
from scp_memory.trust.config import TrustConfig
from scp_memory.trust.relation import Relation, lexical_relation


def _t(text: str) -> set[str]:
    return tokenize(text)


def test_unrelated_memories_are_neutral():
    rel = lexical_relation(_t("user prefers dark mode"), _t("the cat sat outside"), threshold=0.5)
    assert rel is Relation.NEUTRAL


def test_similar_same_polarity_agree():
    rel = lexical_relation(
        _t("user prefers dark mode"), _t("user prefers dark mode theme"), threshold=0.5
    )
    assert rel is Relation.AGREE


def test_similar_divergent_polarity_conflict():
    # Divergent polarity with overlap still above threshold flips agree → conflict.
    rel = lexical_relation(
        _t("user wants email notifications"),
        _t("user wants no email notifications"),
        threshold=0.5,
    )
    assert rel is Relation.CONFLICT


def test_lexical_detector_matches_pure_relation():
    config = TrustConfig()
    detector = LexicalRelationDetector()

    class _M:
        def __init__(self, content: str) -> None:
            self.content = content

    a, b = _M("user prefers dark mode"), _M("user prefers dark mode theme")
    rel = detector.relate(a, b, _t(a.content), _t(b.content), config=config)
    assert rel is lexical_relation(
        _t(a.content), _t(b.content), threshold=config.corroboration_threshold
    )


def test_default_detector_is_lexical(monkeypatch):
    # Default config keeps the hermetic lexical detector (no model load).
    get_relation_detector.cache_clear()
    assert get_relation_detector().name == "lexical"
