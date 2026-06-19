"""Embeddings — pure, deterministic, dependency-free (13-retrieval-model).

Phase 3 needs *semantic* vectors but must run with no external model or service
on the default/test path. ``HashingEmbedder`` maps text to a fixed-dimension unit
vector via token feature-hashing (the "hashing trick"). It is deterministic and
cheap, so query and document vectors are always consistent and reproducible.

This is a deliberate stand-in: the ``Embedder`` protocol is the seam where a real
model (sentence-transformers, a hosted embedding API) drops in for production
without touching retrieval, ranking, or the vector backend.
"""

import hashlib
import math
from typing import Protocol

from scp_memory.intelligence.similarity import tokenize


class Embedder(Protocol):
    """Maps text to a fixed-dimension vector. Implementations are deterministic."""

    dim: int

    def embed(self, text: str) -> list[float]: ...


def _bucket(token: str, dim: int) -> int:
    """Hash a token to a vector index in [0, dim)."""
    digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big") % dim


def _sign(token: str) -> float:
    """A second, independent hash → signed contribution (reduces collision bias)."""
    digest = hashlib.blake2b(token.encode("utf-8"), digest_size=1, person=b"sign").digest()
    return 1.0 if digest[0] & 1 else -1.0


class HashingEmbedder:
    """Feature-hashing bag-of-tokens embedder producing L2-normalized vectors."""

    def __init__(self, dim: int = 256) -> None:
        if dim <= 0:
            raise ValueError("dim must be positive")
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        """Return the L2-normalized hashed vector; a token-free text maps to zeros."""
        vec = [0.0] * self.dim
        for token in tokenize(text):
            vec[_bucket(token, self.dim)] += _sign(token)
        norm = math.sqrt(sum(v * v for v in vec))
        if norm == 0.0:
            return vec
        return [v / norm for v in vec]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine of two equal-length vectors, clamped to [0, 1].

    Both inputs are expected L2-normalized, so this is their dot product; negative
    (anti-correlated) values are clamped to 0.0 — "no similarity".
    """
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    return max(0.0, min(1.0, dot))
