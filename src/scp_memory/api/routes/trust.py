"""Trust explainability endpoint (Phase 4): why is a memory trusted?

Returns a single memory's decomposable trust verdict — provenance quality,
confidence, freshness, the composite score, and a plain-language explanation —
computed against its active, same-type namespace neighbours (15-trust-model).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from scp_memory.api.deps import get_db
from scp_memory.metrics import TRUST_EVALUATIONS
from scp_memory.schemas.retrieval import TrustBreakdown
from scp_memory.services import trust_service

router = APIRouter(prefix="/v1/trust", tags=["trust"])


@router.get("/{memory_id}", response_model=TrustBreakdown)
def explain_trust(
    memory_id: str,
    namespace: str = Query(..., min_length=1, description="Tenant/owner scope (required)."),
    db: Session = Depends(get_db),
) -> TrustBreakdown:
    result = trust_service.evaluate_memory(db, memory_id=memory_id, namespace=namespace)
    if result is None:
        raise HTTPException(status_code=404, detail="memory not found in namespace")
    TRUST_EVALUATIONS.inc()
    return TrustBreakdown(
        provenance_quality=result.provenance_quality,
        confidence=result.confidence,
        freshness=result.freshness,
        score=result.score,
        explanation=result.explanation,
    )
