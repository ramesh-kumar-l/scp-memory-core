"""MemoryRelation ORM model — graph edges between memories (11-data-models).

Phase 1 defines the table only; edge creation (consolidation, supersession)
arrives with Phase 2. Mirrors the NetworkX graph layer.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from scp_memory.db.base import Base
from scp_memory.models.ids import new_relation_id
from scp_memory.utils.time import utcnow


class MemoryRelation(Base):
    __tablename__ = "memory_relations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_relation_id)
    src_id: Mapped[str] = mapped_column(ForeignKey("memories.id", ondelete="CASCADE"))
    dst_id: Mapped[str] = mapped_column(ForeignKey("memories.id", ondelete="CASCADE"))
    relation: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

    __table_args__ = (Index("ix_relations_src", "src_id"),)
