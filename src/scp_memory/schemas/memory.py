"""Memory request/response schemas (Pydantic v2, ADR-003).

`metadata` in the API maps to the ORM attribute `meta` (the latter avoids the
reserved declarative name).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from scp_memory.models.enums import MemoryState, MemoryType


class MemoryCreate(BaseModel):
    """Payload to create a memory."""

    content: str = Field(min_length=1)
    namespace: str = Field(min_length=1, description="Tenant/owner scope.")
    type: MemoryType = MemoryType.fact
    metadata: dict = Field(default_factory=dict)
    source: str | None = Field(default=None, description="Provenance source, e.g. 'settings'.")


class MemoryUpdate(BaseModel):
    """Partial update. Omitted fields are left unchanged."""

    content: str | None = Field(default=None, min_length=1)
    type: MemoryType | None = None
    metadata: dict | None = None


class MemoryRead(BaseModel):
    """Memory as returned by the API."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    content: str
    type: MemoryType
    state: MemoryState
    importance: float | None = None
    access_count: int = 0
    namespace: str
    metadata: dict = Field(default_factory=dict, validation_alias="meta")
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime | None = None


class MemoryList(BaseModel):
    """Paged list of memories."""

    items: list[MemoryRead]
    total: int
    limit: int
    offset: int
