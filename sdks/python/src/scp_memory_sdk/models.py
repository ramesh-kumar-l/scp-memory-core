"""Typed response models mirroring the API schemas (1:1 with src/scp_memory/schemas).

Plain dataclasses with ``from_dict`` factories. Timestamps stay as ISO-8601
strings (no implicit tz parsing); unknown keys are ignored so a newer server
stays compatible with an older client.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Memory:
    id: str
    content: str
    type: str
    state: str
    namespace: str
    importance: float | None
    access_count: int
    metadata: dict[str, Any]
    created_at: str
    updated_at: str
    last_accessed_at: str | None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Memory:
        return cls(
            id=d["id"],
            content=d["content"],
            type=d["type"],
            state=d["state"],
            namespace=d["namespace"],
            importance=d.get("importance"),
            access_count=d.get("access_count", 0),
            metadata=d.get("metadata", {}),
            created_at=d["created_at"],
            updated_at=d["updated_at"],
            last_accessed_at=d.get("last_accessed_at"),
        )


@dataclass
class MemoryPage:
    items: list[Memory]
    total: int
    limit: int
    offset: int

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> MemoryPage:
        return cls(
            items=[Memory.from_dict(m) for m in d["items"]],
            total=d["total"],
            limit=d["limit"],
            offset=d["offset"],
        )


@dataclass
class AuditEvent:
    id: str
    memory_id: str
    action: str
    actor: str
    timestamp: str
    diff: dict[str, Any]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> AuditEvent:
        return cls(
            id=d["id"],
            memory_id=d["memory_id"],
            action=d["action"],
            actor=d["actor"],
            timestamp=d["timestamp"],
            diff=d.get("diff", {}),
        )


@dataclass
class AuditLog:
    items: list[AuditEvent]
    total: int

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> AuditLog:
        return cls(items=[AuditEvent.from_dict(e) for e in d["items"]], total=d["total"])


@dataclass
class TrustBreakdown:
    provenance_quality: float
    confidence: float
    freshness: float
    score: float
    explanation: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TrustBreakdown:
        return cls(
            provenance_quality=d["provenance_quality"],
            confidence=d["confidence"],
            freshness=d["freshness"],
            score=d["score"],
            explanation=d["explanation"],
        )


@dataclass
class SignalScores:
    keyword: float
    vector: float
    metadata: float
    importance: float
    trust: float

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SignalScores:
        return cls(
            keyword=d["keyword"],
            vector=d["vector"],
            metadata=d["metadata"],
            importance=d["importance"],
            trust=d["trust"],
        )


@dataclass
class SearchResult:
    memory: Memory
    score: float
    signals: SignalScores
    weights: dict[str, float]
    trust: TrustBreakdown

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SearchResult:
        return cls(
            memory=Memory.from_dict(d["memory"]),
            score=d["score"],
            signals=SignalScores.from_dict(d["signals"]),
            weights=d["weights"],
            trust=TrustBreakdown.from_dict(d["trust"]),
        )


@dataclass
class SearchResponse:
    query: str
    namespace: str
    mode: str
    count: int
    results: list[SearchResult] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SearchResponse:
        return cls(
            query=d["query"],
            namespace=d["namespace"],
            mode=d["mode"],
            count=d["count"],
            results=[SearchResult.from_dict(r) for r in d["results"]],
        )


@dataclass
class DecayResult:
    namespace: str
    scanned: int
    decayed: list[str]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> DecayResult:
        return cls(namespace=d["namespace"], scanned=d["scanned"], decayed=d["decayed"])


@dataclass
class DedupCluster:
    canonical: str
    merged: list[str]


@dataclass
class DedupResult:
    namespace: str
    clusters: list[DedupCluster]
    merged_count: int

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> DedupResult:
        return cls(
            namespace=d["namespace"],
            clusters=[DedupCluster(c["canonical"], c["merged"]) for c in d["clusters"]],
            merged_count=d["merged_count"],
        )


@dataclass
class ConsolidateResult:
    summary: Memory
    source_ids: list[str]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ConsolidateResult:
        return cls(summary=Memory.from_dict(d["summary"]), source_ids=d["source_ids"])
