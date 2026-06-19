"""Hybrid retrieval endpoint (Phase 3): keyword + vector + metadata + ranking.

Returns ranked, **explainable** results — each carries its per-signal scores and
the weights that produced its position (13-retrieval-model, 14-ranking-model).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from scp_memory.api.deps import get_db
from scp_memory.schemas.memory import MemoryRead
from scp_memory.schemas.retrieval import (
    RetrievedMemory,
    RetrieveRequest,
    RetrieveResponse,
    SignalScores,
    TrustBreakdown,
)
from scp_memory.services import retrieval_service

router = APIRouter(prefix="/v1/retrieval", tags=["retrieval"])


@router.post("/search", response_model=RetrieveResponse)
def search(payload: RetrieveRequest, db: Session = Depends(get_db)) -> RetrieveResponse:
    ranked = retrieval_service.search(db, payload)
    return RetrieveResponse(
        query=payload.query,
        namespace=payload.namespace,
        mode=payload.mode,
        count=len(ranked),
        results=[
            RetrievedMemory(
                memory=MemoryRead.model_validate(r.memory),
                score=r.score,
                signals=SignalScores(**r.signals),
                weights=r.weights,
                trust=TrustBreakdown(
                    provenance_quality=r.trust.provenance_quality,
                    confidence=r.trust.confidence,
                    freshness=r.trust.freshness,
                    score=r.trust.score,
                    explanation=r.trust.explanation,
                ),
            )
            for r in ranked
        ],
    )
