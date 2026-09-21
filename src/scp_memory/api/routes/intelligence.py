"""Memory intelligence endpoints (Phase 2): decay, dedup, consolidate.

These trigger batch self-management passes over a namespace. Importance itself is
maintained automatically on create/access and surfaced on every `MemoryRead`.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from scp_memory.api.deps import get_actor, get_db
from scp_memory.schemas.common import ErrorResponse
from scp_memory.schemas.intelligence import (
    ConsolidateRequest,
    ConsolidateResult,
    DecayResult,
    DedupClusterRead,
    DedupResult,
    NamespaceRequest,
)
from scp_memory.schemas.memory import MemoryRead
from scp_memory.services import consolidation_service, decay_service, dedup_service

router = APIRouter(prefix="/v1/intelligence", tags=["intelligence"])


@router.post("/decay", response_model=DecayResult)
def run_decay(payload: NamespaceRequest, db: Session = Depends(get_db)) -> DecayResult:
    scanned, decayed = decay_service.run(
        db, namespace=payload.namespace, threshold=payload.threshold
    )
    return DecayResult(namespace=payload.namespace, scanned=scanned, decayed=decayed)


@router.post("/dedup", response_model=DedupResult)
def run_dedup(payload: NamespaceRequest, db: Session = Depends(get_db)) -> DedupResult:
    clusters = dedup_service.run(db, namespace=payload.namespace, threshold=payload.threshold)
    return DedupResult(
        namespace=payload.namespace,
        clusters=[
            DedupClusterRead(canonical=c.canonical_id, merged=c.merged_ids) for c in clusters
        ],
        merged_count=sum(len(c.merged_ids) for c in clusters),
    )


@router.post(
    "/consolidate",
    response_model=ConsolidateResult,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
def run_consolidate(
    payload: ConsolidateRequest,
    db: Session = Depends(get_db),
    actor: str = Depends(get_actor),
) -> ConsolidateResult:
    memory = consolidation_service.consolidate(
        db,
        namespace=payload.namespace,
        source_ids=payload.source_ids,
        summary=payload.summary,
        actor=actor,
    )
    return ConsolidateResult(
        summary=MemoryRead.model_validate(memory),
        source_ids=payload.source_ids,
    )
