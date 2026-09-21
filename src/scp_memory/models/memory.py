"""Memory ORM model — the central entity (11-data-models, 12-memory-model).

The relational record is the source of truth; vector/graph projections (later
phases) are derived from it.
"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from scp_memory.db.base import Base
from scp_memory.models.enums import MemoryState, MemoryType
from scp_memory.models.ids import new_memory_id
from scp_memory.utils.time import utcnow


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_memory_id)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False, default=MemoryType.fact.value)
    state: Mapped[str] = mapped_column(String, nullable=False, default=MemoryState.active.value)
    # Derived importance in [0, 1] (Phase 2). Set at create, refreshed on access.
    importance: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Access frequency signal for importance scoring (Phase 2).
    access_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    namespace: Mapped[str] = mapped_column(String, nullable=False)
    # `metadata` is reserved on the declarative class, so the attribute is `meta`.
    meta: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )
    last_accessed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    provenance: Mapped["Provenance"] = relationship(  # noqa: F821
        back_populates="memory",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (Index("ix_memories_namespace_state", "namespace", "state"),)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Memory id={self.id} ns={self.namespace} state={self.state}>"
