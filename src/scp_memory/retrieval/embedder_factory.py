"""Embedder selection (ADR-011): hashing stand-in (default) or a local model.

Keeps the choice in one place so retrieval/vector code depends only on the
``Embedder`` protocol, never on a concrete implementation. Selection is driven by
``SCP_EMBEDDER`` (see ``config.Settings``). An explicit ``sentence-transformers``
selection that cannot load fails loudly rather than silently degrading to a
weaker embedder.
"""

import logging

from scp_memory.config import Settings, get_settings
from scp_memory.retrieval.config import RetrievalConfig
from scp_memory.retrieval.embedding import Embedder, HashingEmbedder

logger = logging.getLogger("scp_memory.retrieval.embedding")

_SENTENCE_TRANSFORMERS = {"sentence-transformers", "sentence_transformers", "st"}
_HASHING = {"hashing", "hash", "default"}


def build_embedder(
    settings: Settings | None = None,
    *,
    config: RetrievalConfig | None = None,
) -> Embedder:
    """Return the configured embedder (default: the hashing stand-in)."""
    settings = settings or get_settings()
    config = config or RetrievalConfig()
    choice = settings.embedder.lower()
    if choice in _SENTENCE_TRANSFORMERS:
        from scp_memory.retrieval.local_embedder import SentenceTransformerEmbedder

        return SentenceTransformerEmbedder(
            settings.embedding_model, offline=settings.embedding_offline
        )
    if choice not in _HASHING:
        logger.warning("unknown SCP_EMBEDDER=%r; using the hashing stand-in", settings.embedder)
    return HashingEmbedder(dim=config.embedding_dim)
