"""Request/response schemas for the hybrid retrieval endpoint (Phase 3).

Every result is explainable: it carries the per-signal scores and the weights
that produced its rank (14-ranking-model).
"""

from typing import Literal

from pydantic import BaseModel, Field

from scp_memory.models.enums import MemoryState, MemoryType
from scp_memory.schemas.memory import MemoryRead


class RetrieveRequest(BaseModel):
    """A retrieval query with metadata constraints and a fusion mode."""

    query: str = Field(min_length=1)
    namespace: str = Field(min_length=1, description="Tenant/owner scope (required).")
    k: int = Field(default=10, ge=1, le=100, description="Top-k results to return.")
    mode: Literal["keyword", "vector", "hybrid"] = "hybrid"
    type: MemoryType | None = Field(default=None, description="Restrict to a memory type.")
    state: MemoryState | None = Field(default=None, description="Defaults to active.")
    min_confidence: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Drop results below this trust confidence."
    )


class SignalScores(BaseModel):
    """Per-signal contributions behind a result's rank (normalized where applicable)."""

    keyword: float
    vector: float
    metadata: float
    importance: float
    trust: float


class TrustBreakdown(BaseModel):
    """Decomposable trust verdict for a memory (15-trust-model)."""

    provenance_quality: float
    confidence: float
    freshness: float
    score: float
    explanation: str


class RetrievedMemory(BaseModel):
    memory: MemoryRead
    score: float
    signals: SignalScores
    weights: dict[str, float]
    trust: TrustBreakdown


class RetrieveResponse(BaseModel):
    query: str
    namespace: str
    mode: str
    count: int
    results: list[RetrievedMemory]
