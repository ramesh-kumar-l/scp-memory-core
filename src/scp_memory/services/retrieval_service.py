"""Hybrid retrieval orchestration (13-retrieval-model, 14-ranking-model).

Pipeline: metadata filter (SQL) → keyword candidates ∪ vector candidates → fuse
signals → rank → explainable results. Importance (Phase 2) is a ranking signal.

The relational store is the source of truth; the vector backend is a derived
index. Retrieving touches the returned top-k (``last_accessed_at`` / frequency),
feeding the Phase-2 importance/decay loop.
"""

import logging
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from scp_memory.metrics import RETRIEVAL_QUERIES
from scp_memory.models.enums import MemoryState
from scp_memory.models.memory import Memory
from scp_memory.observability.spans import span
from scp_memory.retrieval.config import RetrievalConfig
from scp_memory.retrieval.embedder_factory import build_embedder
from scp_memory.retrieval.fusion import rrf_fuse, weighted_fuse
from scp_memory.schemas.retrieval import RetrieveRequest
from scp_memory.services import importance_service, trust_service
from scp_memory.services.keyword_backend import get_keyword_backend
from scp_memory.services.trust_service import TrustResult
from scp_memory.services.vector_backend import get_backend
from scp_memory.utils.time import utcnow

logger = logging.getLogger("scp_memory.retrieval")

_CONFIG = RetrievalConfig()
_EMBEDDER = build_embedder(config=_CONFIG)  # hashing by default; SCP_EMBEDDER selects a model


@dataclass
class RankedMemory:
    """A retrieved memory with its fused score, per-signal scores, and trust verdict."""

    memory: Memory
    score: float
    signals: dict[str, float]
    weights: dict[str, float]
    trust: TrustResult


def _candidates(
    db: Session, *, namespace: str, type_: str | None, state: str | None, limit: int
) -> list[Memory]:
    filters = [Memory.namespace == namespace, Memory.state == (state or MemoryState.active.value)]
    if type_ is not None:
        filters.append(Memory.type == type_)
    return list(
        db.scalars(
            select(Memory)
            .options(selectinload(Memory.provenance))  # avoid N+1 in trust scoring
            .where(*filters)
            .order_by(Memory.importance.desc(), Memory.created_at.desc())
            .limit(limit)
        )
    )


def _touch(db: Session, memories: list[Memory]) -> None:
    """Record access on retrieved results, refreshing the Phase-2 importance signal."""
    now = utcnow()
    for memory in memories:
        memory.last_accessed_at = now
        memory.access_count = (memory.access_count or 0) + 1
        importance_service.recompute(memory, now=now)
    db.commit()


def _fuse(
    items: list[Memory],
    keyword: list[float],
    vector: list[float],
    importance: list[float],
    trust: list[float],
    method: str,
) -> list[tuple[float, dict[str, float]]]:
    """Combine signals by the requested method (default weighted-linear, or RRF)."""
    if method == "rrf":
        return rrf_fuse(
            [m.id for m in items],
            {"keyword": keyword, "vector": vector, "importance": importance, "trust": trust},
        )
    return weighted_fuse(keyword, vector, importance, _CONFIG.weights, trust=trust)


def search(
    db: Session, req: RetrieveRequest, *, touch: bool = True, fuse_method: str = "weighted"
) -> list[RankedMemory]:
    """Run hybrid retrieval and return ranked, explainable results.

    ``fuse_method`` selects score fusion: ``"weighted"`` (default, explainable
    min-max weighted linear) or ``"rrf"`` (reciprocal-rank fusion). The choice is an
    internal/benchmark knob (evals/run_retrieval_benchmark.py); the public API
    contract is unchanged.
    """
    state = req.state.value if req.state else None
    type_ = req.type.value if req.type else None
    with span("retrieval.candidates", **{"scp.namespace": req.namespace, "scp.mode": req.mode}):
        candidates = _candidates(
            db, namespace=req.namespace, type_=type_, state=state, limit=_CONFIG.candidate_limit
        )
    RETRIEVAL_QUERIES.labels(mode=req.mode).inc()
    if not candidates:
        return []

    by_id: dict[str, Memory] = {m.id: m for m in candidates}

    # Vector candidates: may surface ids beyond the keyword window (e.g. ANN).
    vscore: dict[str, float] = {}
    if req.mode in ("vector", "hybrid"):
        with span("retrieval.vector", **{"scp.backend": get_backend().name}):
            hits = get_backend().search(
                query=req.query,
                namespace=req.namespace,
                type_=type_,
                candidates=candidates,
                embedder=_EMBEDDER,
                k=_CONFIG.candidate_limit,
            )
            for hit in hits:
                vscore[hit.memory_id] = hit.score
                if hit.memory_id not in by_id:
                    extra = db.get(Memory, hit.memory_id)
                    if extra is not None:
                        by_id[hit.memory_id] = extra

    items = list(by_id.values())
    keyword_backend = get_keyword_backend()
    with span(
        "retrieval.keyword", **{"scp.candidates": len(items), "scp.backend": keyword_backend.name}
    ):
        if req.mode in ("keyword", "hybrid"):
            kw = keyword_backend.scores(
                db=db, query=req.query, namespace=req.namespace, type_=type_, candidates=items
            )
            keyword = [kw.get(m.id, 0.0) for m in items]
        else:
            keyword = [0.0] * len(items)
    vector = [vscore.get(m.id, 0.0) for m in items]
    importance = [m.importance or 0.0 for m in items]

    # Trust layer (Phase 4): provenance/confidence/freshness per candidate, fused
    # as an extra ranking dimension and carried on each result for explainability.
    with span("retrieval.trust", **{"scp.candidates": len(items)}):
        trust_results = trust_service.evaluate_all(items)
    trust = [t.score for t in trust_results]

    weights = {
        "keyword": _CONFIG.weights.keyword,
        "vector": _CONFIG.weights.vector,
        "importance": _CONFIG.weights.importance,
        "trust": _CONFIG.weights.trust,
    }
    with span("retrieval.fuse", **{"scp.method": fuse_method}):
        ranked: list[RankedMemory] = []
        for memory, t_result, (score, parts) in zip(
            items,
            trust_results,
            _fuse(items, keyword, vector, importance, trust, fuse_method),
            strict=True,
        ):
            ranked.append(
                RankedMemory(
                    memory=memory,
                    score=round(score, 4),
                    signals={**parts, "metadata": 1.0},
                    weights=weights,
                    trust=t_result,
                )
            )

        if req.min_confidence is not None:
            ranked = [r for r in ranked if r.trust.confidence >= req.min_confidence]
        ranked.sort(key=lambda r: (r.score, r.memory.importance or 0.0), reverse=True)

    top = ranked[: min(req.k, _CONFIG.max_k)]
    if touch and top:
        _touch(db, [r.memory for r in top])
    return top
