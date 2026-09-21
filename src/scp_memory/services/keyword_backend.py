"""Keyword search backends (13-retrieval-model).

Lexical relevance has two implementations behind one seam, mirroring the vector
backend:

- ``InProcessBM25Backend`` (default) — Okapi BM25 over the metadata-filtered
  candidate set, idf derived from that set. Zero-infra, deterministic, hermetic;
  O(N) per query, fine at MVP scale. The tested default path.
- Inverted-index backends (scale path) — a persistent index does the lexical
  matching/ranking in the store: ``Fts5Backend`` (SQLite FTS5) and
  ``TsvectorBackend`` (PostgreSQL GIN tsvector). Selected by
  ``SCP_KEYWORD_BACKEND``; loaded lazily so the default path never imports them.

All backends return ``{memory_id: score}`` for the candidate set (higher = more
relevant). Retrieval aligns that onto the candidate array, so the seam is a pure
swap — fusion, trust, and explainability are unchanged.
"""

import logging
from functools import lru_cache
from typing import Protocol

from scp_memory.config import get_settings
from scp_memory.intelligence.similarity import tokenize
from scp_memory.models.memory import Memory
from scp_memory.retrieval.keyword import bm25_scores

logger = logging.getLogger("scp_memory.retrieval.keyword")


class KeywordBackend(Protocol):
    """Scores candidates by lexical relevance to ``query`` (higher = better)."""

    name: str

    def scores(
        self,
        *,
        db: object,
        query: str,
        namespace: str,
        type_: str | None,
        candidates: list[Memory],
    ) -> dict[str, float]: ...


class InProcessBM25Backend:
    """Okapi BM25 over the candidate set, computed in-process (the default)."""

    name = "bm25"

    def scores(
        self,
        *,
        db: object,
        query: str,
        namespace: str,
        type_: str | None,
        candidates: list[Memory],
    ) -> dict[str, float]:
        q_tokens = list(tokenize(query))
        docs = [list(tokenize(m.content)) for m in candidates]
        raw = bm25_scores(q_tokens, docs)
        return {m.id: s for m, s in zip(candidates, raw, strict=True)}


@lru_cache
def get_keyword_backend() -> KeywordBackend:
    """Resolve the configured keyword backend (cached for the process)."""
    backend = get_settings().keyword_backend.lower()
    if backend == "fts5":  # pragma: no cover - integration-only
        from scp_memory.services.fts5_backend import Fts5Backend

        logger.info("keyword backend: fts5")
        return Fts5Backend()
    if backend == "tsvector":  # pragma: no cover - integration-only
        from scp_memory.services.tsvector_backend import TsvectorBackend

        logger.info("keyword backend: tsvector")
        return TsvectorBackend()
    return InProcessBM25Backend()
