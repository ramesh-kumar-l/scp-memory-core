"""AuditEvent ORM model — append-only mutation log (16-security-model).

`memory_id` is intentionally NOT a foreign key: the audit trail must survive a
hard-delete of the memory it describes.
"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from scp_memory.db.base import Base
from scp_memory.models.ids import new_event_id
from scp_memory.utils.time import utcnow


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_event_id)
    memory_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    action: Mapped[str] = mapped_column(String, nullable=False)
    actor: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, index=True
    )
    diff: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    __table_args__ = (Index("ix_audit_memory_ts", "memory_id", "timestamp"),)
