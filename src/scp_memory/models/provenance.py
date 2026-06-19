"""Provenance ORM model — where a memory came from (04-domain-model).

Provenance is never lost; consolidation (Phase 2) records source IDs in
`derivation`.
"""

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from scp_memory.db.base import Base


class Provenance(Base):
    __tablename__ = "provenance"

    memory_id: Mapped[str] = mapped_column(
        ForeignKey("memories.id", ondelete="CASCADE"), primary_key=True
    )
    source: Mapped[str] = mapped_column(String, nullable=False, default="user")
    actor: Mapped[str] = mapped_column(String, nullable=False, default="system")
    derivation: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    memory: Mapped["Memory"] = relationship(back_populates="provenance")  # noqa: F821
