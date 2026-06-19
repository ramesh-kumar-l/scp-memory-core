"""Memory CRUD + audit endpoints (10-api-contracts, Phase 1)."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from scp_memory.api.deps import get_actor, get_db
from scp_memory.schemas.audit import AuditEventRead, AuditList
from scp_memory.schemas.common import ErrorResponse
from scp_memory.schemas.memory import (
    MemoryCreate,
    MemoryList,
    MemoryRead,
    MemoryUpdate,
)
from scp_memory.services import audit_service, memory_service

router = APIRouter(prefix="/v1/memories", tags=["memories"])

_NOT_FOUND = {404: {"model": ErrorResponse}}


@router.post("", response_model=MemoryRead, status_code=status.HTTP_201_CREATED)
def create_memory(
    payload: MemoryCreate,
    db: Session = Depends(get_db),
    actor: str = Depends(get_actor),
) -> MemoryRead:
    memory = memory_service.create(db, payload, actor=actor)
    return MemoryRead.model_validate(memory)


@router.get("", response_model=MemoryList)
def list_memories(
    namespace: str = Query(..., min_length=1),
    type: str | None = Query(default=None),
    state: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> MemoryList:
    items, total = memory_service.list_memories(
        db, namespace=namespace, type_=type, state=state, limit=limit, offset=offset
    )
    return MemoryList(
        items=[MemoryRead.model_validate(m) for m in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{memory_id}", response_model=MemoryRead, responses=_NOT_FOUND)
def get_memory(
    memory_id: str,
    namespace: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> MemoryRead:
    memory = memory_service.get(db, memory_id, namespace=namespace)
    return MemoryRead.model_validate(memory)


@router.patch("/{memory_id}", response_model=MemoryRead, responses=_NOT_FOUND)
def update_memory(
    memory_id: str,
    payload: MemoryUpdate,
    namespace: str | None = Query(default=None),
    db: Session = Depends(get_db),
    actor: str = Depends(get_actor),
) -> MemoryRead:
    memory = memory_service.update(db, memory_id, payload, actor=actor, namespace=namespace)
    return MemoryRead.model_validate(memory)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT, responses=_NOT_FOUND)
def delete_memory(
    memory_id: str,
    hard: bool = Query(default=False, description="Hard-delete for compliance erasure."),
    namespace: str | None = Query(default=None),
    db: Session = Depends(get_db),
    actor: str = Depends(get_actor),
) -> Response:
    memory_service.delete(db, memory_id, actor=actor, hard=hard, namespace=namespace)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{memory_id}/audit", response_model=AuditList)
def get_memory_audit(
    memory_id: str,
    db: Session = Depends(get_db),
) -> AuditList:
    events, total = audit_service.list_for_memory(db, memory_id)
    return AuditList(
        items=[AuditEventRead.model_validate(e) for e in events],
        total=total,
    )
