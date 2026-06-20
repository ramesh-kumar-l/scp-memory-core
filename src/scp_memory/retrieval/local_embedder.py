"""Local, offline semantic embeddings via sentence-transformers (ADR-011).

The default ``HashingEmbedder`` is a deterministic stand-in; this is the
production seam — a real model that runs **entirely on-device**, with no embedding
API calls ever. ``all-MiniLM-L6-v2`` (384-dim) is the de-facto local-embedding
baseline: small (~80 MB), CPU-friendly, and well-supported.

The model is an optional dependency (``pip install scp-memory-core[embeddings]``)
and is imported lazily, so the default/test path never requires it. With
``offline=True`` the HuggingFace loader is pinned to the local cache, so an
air-gapped deployment runs against a pre-downloaded model and never touches the
network. It satisfies the ``Embedder`` protocol (``dim`` + ``embed``), so
retrieval, ranking, and the vector backend are unchanged.
"""

import logging
import os

logger = logging.getLogger("scp_memory.retrieval.embedding")


class SentenceTransformerEmbedder:
    """A sentence-transformers model behind the ``Embedder`` protocol."""

    def __init__(
        self,
        model: str = "sentence-transformers/all-MiniLM-L6-v2",
        *,
        offline: bool = True,
    ) -> None:
        if offline:
            # Pin the loader to the local cache: no implicit network at load time.
            os.environ.setdefault("HF_HUB_OFFLINE", "1")
            os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:  # pragma: no cover - import guard
            raise RuntimeError(
                "sentence-transformers is not installed; install the [embeddings] extra "
                "(pip install scp-memory-core[embeddings]) to use SCP_EMBEDDER="
                "sentence-transformers."
            ) from exc
        self._model = SentenceTransformer(model)
        # Method was renamed across versions; support both for forward-compat.
        dim_of = getattr(self._model, "get_embedding_dimension", None) or (
            self._model.get_sentence_embedding_dimension
        )
        self.dim = int(dim_of())
        logger.info("embedder: sentence-transformers model=%s dim=%d", model, self.dim)

    def embed(self, text: str) -> list[float]:
        """Return the L2-normalized embedding for ``text`` (consistent with cosine)."""
        vec = self._model.encode(text, normalize_embeddings=True)
        return [float(x) for x in vec.tolist()]
