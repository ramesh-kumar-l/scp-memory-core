"""Trust evaluation — DB-aware orchestration (Phase 4, 15-trust-model).

Combines the pure trust scorers (``scp_memory.trust``) with relational facts —
provenance source, age, and namespace neighbours — into an explainable per-memory
trust verdict. Trust augments ranking (14-ranking-model) and travels with every
retrieval result; it never silently hides memories.

Corroboration/contradiction here defaults to a **lexical stand-in**: token-overlap
for agreement and negation-polarity divergence for conflict. This mirrors the
Phase-2 dedup approach (honest, hermetic, zero-infra). The decision is delegated
to a ``RelationDetector`` (``services.relation_detector``), so a semantic NLI
detector swaps in behind ``SCP_TRUST_NLI`` without changing the trust contract.
The service never mutates the database.
"""

import logging
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from scp_memory.intelligence.similarity import tokenize
from scp_memory.models.enums import MemoryState
from scp_memory.models.memory import Memory
from scp_memory.services.relation_detector import RelationDetector, get_relation_detector
from scp_memory.trust.confidence import confidence_score
from scp_memory.trust.config import TrustConfig
from scp_memory.trust.explain import explain
from scp_memory.trust.freshness import freshness_score
from scp_memory.trust.provenance import provenance_quality
from scp_memory.trust.relation import Relation
from scp_memory.trust.score import trust_score
from scp_memory.utils.time import utcnow

logger = logging.getLogger("scp_memory.trust")

_CONFIG = TrustConfig()


@dataclass
class TrustResult:
    """A memory's decomposable trust verdict (15-trust-model)."""

    provenance_quality: float
    confidence: float
    freshness: float
    score: float
    explanation: str


def _age_seconds(created: datetime | None, now: datetime) -> float:
    """Age in seconds, tolerant of naive (SQLite) vs aware datetimes."""
    if created is None:
        return 0.0
    if created.tzinfo is None and now.tzinfo is not None:
        now = now.replace(tzinfo=None)
    elif created.tzinfo is not None and now.tzinfo is None:
        created = created.replace(tzinfo=None)
    return max(0.0, (now - created).total_seconds())


def _source_of(memory: Memory) -> str | None:
    prov = memory.provenance
    return prov.source if prov is not None else None


def _token_map(memories: list[Memory]) -> dict[str, set[str]]:
    """Tokenize each memory once; corroboration scans are O(N²) comparisons, O(N) tokenizations."""
    return {m.id: tokenize(m.content) for m in memories}


def _counts(
    memory: Memory,
    neighbors: list[Memory],
    tokens: dict[str, set[str]],
    config: TrustConfig,
    detector: RelationDetector,
) -> tuple[int, int]:
    corroboration = contradiction = 0
    for other in neighbors:
        if other.id == memory.id or other.type != memory.type:
            continue
        relation = detector.relate(
            memory, other, tokens[memory.id], tokens[other.id], config=config
        )
        if relation is Relation.AGREE:
            corroboration += 1
        elif relation is Relation.CONFLICT:
            contradiction += 1
    return corroboration, contradiction


def _evaluate(
    memory: Memory,
    neighbors: list[Memory],
    tokens: dict[str, set[str]],
    now: datetime,
    config: TrustConfig,
    detector: RelationDetector,
) -> TrustResult:
    source = _source_of(memory)
    pq = provenance_quality(source)
    age_seconds = _age_seconds(memory.created_at, now)
    fresh = freshness_score(age_seconds, config.half_life_for(memory.type))
    corroboration, contradiction = _counts(memory, neighbors, tokens, config, detector)
    confidence = confidence_score(
        provenance_quality=pq,
        corroboration=corroboration,
        contradiction=contradiction,
        saturation=config.corroboration_saturation,
        contradiction_penalty=config.contradiction_penalty,
    )
    score = trust_score(
        provenance_quality=pq, confidence=confidence, freshness=fresh, weights=config.weights
    )
    explanation = explain(
        source=source,
        provenance_quality=pq,
        confidence=confidence,
        freshness=fresh,
        corroboration=corroboration,
        contradiction=contradiction,
        age_days=age_seconds / 86400.0,
    )
    return TrustResult(
        provenance_quality=pq,
        confidence=confidence,
        freshness=fresh,
        score=score,
        explanation=explanation,
    )


def evaluate(
    memory: Memory,
    *,
    neighbors: list[Memory],
    now: datetime | None = None,
    config: TrustConfig = _CONFIG,
    detector: RelationDetector | None = None,
) -> TrustResult:
    """Evaluate one memory's trust against a neighbour pool."""
    now = now or utcnow()
    detector = detector or get_relation_detector()
    pool = list({m.id: m for m in [memory, *neighbors]}.values())
    return _evaluate(memory, neighbors, _token_map(pool), now, config, detector)


def evaluate_all(
    memories: list[Memory],
    *,
    now: datetime | None = None,
    config: TrustConfig = _CONFIG,
    detector: RelationDetector | None = None,
) -> list[TrustResult]:
    """Evaluate trust for each memory using the others as the neighbour pool.

    Aligned with ``memories`` (same order/length) so callers can ``zip`` results
    back onto rows.
    """
    now = now or utcnow()
    detector = detector or get_relation_detector()
    tokens = _token_map(memories)
    return [_evaluate(m, memories, tokens, now, config, detector) for m in memories]


def evaluate_memory(
    db: Session,
    *,
    memory_id: str,
    namespace: str,
    config: TrustConfig = _CONFIG,
) -> TrustResult | None:
    """Explain one memory's trust against its active, same-type namespace neighbours.

    Returns ``None`` if the memory does not exist in the namespace.
    """
    memory = db.get(Memory, memory_id)
    if memory is None or memory.namespace != namespace:
        return None
    neighbors = list(
        db.scalars(
            select(Memory)
            .options(selectinload(Memory.provenance))
            .where(
                Memory.namespace == namespace,
                Memory.state == MemoryState.active.value,
                Memory.type == memory.type,
            )
            .limit(config.neighbor_limit)
        )
    )
    return evaluate(memory, neighbors=neighbors, config=config)
