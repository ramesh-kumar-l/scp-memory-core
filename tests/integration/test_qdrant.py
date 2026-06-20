"""Qdrant vector-backend integration tests (scale-path ANN).

Skipped unless ``SCP_TEST_QDRANT_URL`` points at a reachable Qdrant — set in CI
(services: qdrant) with the ``[vector]`` extra installed. Proves the relational
store can be (re)indexed into Qdrant and that ANN search returns the seeded
memories. Marked ``qdrant`` so it is opt-in.
"""

import os

import pytest

from scp_memory.models.enums import MemoryType
from scp_memory.retrieval.embedding import HashingEmbedder
from scp_memory.schemas.memory import MemoryCreate
from scp_memory.services import memory_service

pytestmark = pytest.mark.qdrant

QDRANT_URL = os.getenv("SCP_TEST_QDRANT_URL")


@pytest.fixture
def qdrant_backend():
    if not QDRANT_URL:
        pytest.skip("SCP_TEST_QDRANT_URL not set")
    pytest.importorskip("qdrant_client")
    os.environ["SCP_QDRANT_URL"] = QDRANT_URL
    os.environ["SCP_QDRANT_COLLECTION"] = "scp_test_memories"
    from scp_memory.config import get_settings

    get_settings.cache_clear()
    from scp_memory.services.qdrant_backend import QdrantBackend

    return QdrantBackend(embedder=HashingEmbedder())


def test_reindex_and_search(db, qdrant_backend):
    contents = [
        "the capital of france is paris",
        "python is a popular programming language",
        "user prefers dark mode in the editor",
    ]
    memories = [
        memory_service.create(
            db, MemoryCreate(content=c, namespace="qd", type=MemoryType.fact), actor="test"
        )
        for c in contents
    ]
    indexed = qdrant_backend.reindex(db, namespace="qd")
    assert indexed == len(memories)

    hits = qdrant_backend.search(
        query="the capital of france is paris",
        namespace="qd",
        type_=None,
        candidates=memories,
        embedder=HashingEmbedder(),
        k=3,
    )
    assert hits
    # The exact-text memory should be the top ANN hit.
    assert hits[0].memory_id == memories[0].id
