"""Qdrant vector backend — the scale path (ADR-007, 13-retrieval-model).

Native approximate-nearest-neighbour search over persisted embeddings. This
module is imported lazily **only** when ``SCP_VECTOR_BACKEND=qdrant``; it requires
the optional ``[vector]`` extra (``qdrant-client``) and a running Qdrant.

It is integration-only and intentionally **not** exercised by the default test
suite — the in-process ``BruteForceBackend`` is the tested default. The relational
store stays the source of truth; ``reindex`` (re)builds the collection from it.
"""

import uuid

from scp_memory.config import get_settings
from scp_memory.models.memory import Memory
from scp_memory.retrieval.embedding import Embedder, HashingEmbedder
from scp_memory.services.vector_backend import VectorHit

# Stable namespace for deriving Qdrant point ids (which must be int/UUID) from
# our string memory ids. The real memory id is also stored in the payload.
_POINT_NS = uuid.UUID("6f1d3b2a-0000-4000-8000-000000000001")


def _point_id(memory_id: str) -> str:
    return str(uuid.uuid5(_POINT_NS, memory_id))


class QdrantBackend:  # pragma: no cover - integration-only
    """ANN search backed by a Qdrant collection."""

    name = "qdrant"

    def __init__(self, embedder: Embedder | None = None) -> None:
        from qdrant_client import QdrantClient

        settings = get_settings()
        self._client = QdrantClient(url=settings.qdrant_url)
        self._collection = settings.qdrant_collection
        self._embedder = embedder or HashingEmbedder()

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
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        must = [FieldCondition(key="namespace", match=MatchValue(value=namespace))]
        if type_ is not None:
            must.append(FieldCondition(key="type", match=MatchValue(value=type_)))
        results = self._client.search(
            collection_name=self._collection,
            query_vector=embedder.embed(query),
            query_filter=Filter(must=must),
            limit=k,
        )
        return [VectorHit(r.payload["memory_id"], float(r.score)) for r in results]

    def reindex(self, db, *, namespace: str | None = None) -> int:
        """Rebuild the collection from the relational store; returns point count."""
        from qdrant_client.models import Distance, PointStruct, VectorParams
        from sqlalchemy import select

        from scp_memory.models.enums import MemoryState

        self._client.recreate_collection(
            collection_name=self._collection,
            vectors_config=VectorParams(size=self._embedder.dim, distance=Distance.COSINE),
        )
        filters = [Memory.state == MemoryState.active.value]
        if namespace:
            filters.append(Memory.namespace == namespace)
        points = [
            PointStruct(
                id=_point_id(m.id),
                vector=self._embedder.embed(m.content),
                payload={"memory_id": m.id, "namespace": m.namespace, "type": m.type},
            )
            for m in db.scalars(select(Memory).where(*filters))
        ]
        if points:
            self._client.upsert(collection_name=self._collection, points=points)
        return len(points)
