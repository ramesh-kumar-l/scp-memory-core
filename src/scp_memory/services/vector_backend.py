"""Vector search backends (13-retrieval-model).

Retrieval needs nearest-neighbour search over memory embeddings. Two backends sit
behind one seam:

- ``BruteForceBackend`` (default) — embeds the metadata-filtered candidates live
  and scores cosine in-process. Zero external infra; deterministic; hermetic
  tests. O(N) per query — fine at MVP scale.
- Qdrant (scale path) — native ANN over persisted vectors. Loaded lazily only when
  ``SCP_VECTOR_BACKEND=qdrant`` so the default path never imports the client.

``get_backend()`` returns the configured backend (cached for the process).
"""

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Protocol

from scp_memory.config import get_settings
from scp_memory.models.memory import Memory
from scp_memory.retrieval.embedding import Embedder, cosine_similarity

logger = logging.getLogger("scp_memory.retrieval.vector")


@dataclass(frozen=True)
class VectorHit:
    memory_id: str
    score: float


class VectorBackend(Protocol):
    """Returns ``VectorHit``s ranked by semantic similarity to ``query``."""

    name: str

    def search(
        self,
        *,
        query: str,
        namespace: str,
        type_: str | None,
        candidates: list[Memory],
        embedder: Embedder,
        k: int,
    ) -> list[VectorHit]: ...


class BruteForceBackend:
    """Cosine over the metadata-filtered candidates, embedded in-process."""

    name = "bruteforce"

    def search(
        self,
        *,
        query: str,
        namespace: str,
        type_: str | None,
        candidates: list[Memory],
        embedder: Embedder,
        k: int,
    ) -> list[VectorHit]:
        q = embedder.embed(query)
        hits = [
            VectorHit(m.id, cosine_similarity(q, embedder.embed(m.content))) for m in candidates
        ]
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:k]


@lru_cache
def get_backend() -> VectorBackend:
    """Resolve the configured vector backend (cached)."""
    backend = get_settings().vector_backend.lower()
    if backend == "qdrant":  # pragma: no cover - integration-only
        from scp_memory.services.qdrant_backend import QdrantBackend

        logger.info("vector backend: qdrant")
        return QdrantBackend()
    return BruteForceBackend()
