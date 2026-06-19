"""Retrieval configuration — tunable, pure (13/14-*-model).

Operational knobs (which vector backend, Qdrant URL) live in
``scp_memory.config.Settings``; algorithmic knobs (dimensions, k bounds, fusion
weights) live here next to the pure logic they parameterize.
"""

from dataclasses import dataclass, field

from scp_memory.retrieval.fusion import FusionWeights


@dataclass(frozen=True)
class RetrievalConfig:
    embedding_dim: int = 256
    default_k: int = 10
    max_k: int = 100
    candidate_limit: int = 500  # cap SQL candidates per query (latency guard)
    weights: FusionWeights = field(default_factory=FusionWeights)
