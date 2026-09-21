"""Audit response schemas (16-security-model)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from scp_memory.models.enums import AuditAction


class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    memory_id: str
    action: AuditAction
    actor: str
    timestamp: datetime
    diff: dict


class AuditList(BaseModel):
    items: list[AuditEventRead]
    total: int
