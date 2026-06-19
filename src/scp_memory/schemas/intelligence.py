"""Request/response schemas for the intelligence endpoints (Phase 2)."""

from pydantic import BaseModel, Field

from scp_memory.schemas.memory import MemoryRead


class NamespaceRequest(BaseModel):
    """Target a batch intelligence pass at one namespace."""

    namespace: str = Field(min_length=1)
    threshold: float | None = Field(
        default=None, description="Override the configured threshold for this run."
    )


class DecayResult(BaseModel):
    namespace: str
    scanned: int
    decayed: list[str]


class DedupClusterRead(BaseModel):
    canonical: str
    merged: list[str]


class DedupResult(BaseModel):
    namespace: str
    clusters: list[DedupClusterRead]
    merged_count: int


class ConsolidateRequest(BaseModel):
    namespace: str = Field(min_length=1)
    source_ids: list[str] = Field(min_length=2, description="Two or more memories to merge.")
    summary: str | None = Field(default=None, description="Optional summary text; else derived.")


class ConsolidateResult(BaseModel):
    summary: MemoryRead
    source_ids: list[str]
