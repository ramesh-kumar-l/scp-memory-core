"""Deduplication service — merge near-duplicate memories (12-memory-model).

A batch pass over a namespace that clusters active memories of the same type by
lexical similarity ([intelligence.similarity]), keeps one canonical memory per
cluster, and archives the rest with a `supersedes` edge back to the canonical.

Scalability note: the pairwise scan is O(n²) within each (namespace, type) group —
fine for batch maintenance at MVP scale. Phase 3's vector index enables
approximate-nearest-neighbour candidate generation to replace the quadratic scan.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from scp_memory.config import get_settings
from scp_memory.intelligence.similarity import jaccard, tokenize
from scp_memory.metrics import MEMORIES_DEDUPED
from scp_memory.models.enums import AuditAction, MemoryState, RelationType
from scp_memory.models.memory import Memory
from scp_memory.services import audit_service, relation_service

logger = logging.getLogger("scp_memory.dedup")


@dataclass
class DedupCluster:
    canonical_id: str
    merged_ids: list[str]


def _canonical(group: list[Memory]) -> Memory:
    """Most important wins; ties go to the oldest (most established) memory."""
    return max(group, key=lambda m: (m.importance or 0.0, -m.created_at.timestamp()))


def _components(group: list[Memory], threshold: float) -> list[list[Memory]]:
    """Connected components under the similarity threshold (union-find)."""
    parent = {m.id: m.id for m in group}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        parent[find(a)] = find(b)

    tokens = {m.id: tokenize(m.content) for m in group}
    for i in range(len(group)):
        for j in range(i + 1, len(group)):
            a, b = group[i], group[j]
            if jaccard(tokens[a.id], tokens[b.id]) >= threshold:
                union(a.id, b.id)

    buckets: dict[str, list[Memory]] = defaultdict(list)
    for m in group:
        buckets[find(m.id)].append(m)
    return list(buckets.values())


def run(
    db: Session,
    *,
    namespace: str,
    threshold: float | None = None,
) -> list[DedupCluster]:
    """Merge duplicate clusters in a namespace; returns the clusters acted on."""
    if threshold is None:
        threshold = get_settings().dedup_similarity_threshold

    rows = list(
        db.scalars(
            select(Memory).where(
                Memory.namespace == namespace,
                Memory.state == MemoryState.active.value,
            )
        )
    )

    by_type: dict[str, list[Memory]] = defaultdict(list)
    for memory in rows:
        by_type[memory.type].append(memory)

    clusters: list[DedupCluster] = []
    for group in by_type.values():
        if len(group) < 2:
            continue
        for component in _components(group, threshold):
            if len(component) < 2:
                continue
            canonical = _canonical(component)
            merged_ids: list[str] = []
            for memory in component:
                if memory.id == canonical.id:
                    continue
                memory.state = MemoryState.archived.value
                relation_service.add(
                    db,
                    src_id=canonical.id,
                    dst_id=memory.id,
                    relation=RelationType.supersedes,
                )
                audit_service.record(
                    db,
                    memory_id=memory.id,
                    action=AuditAction.deduplicate,
                    actor="system",
                    diff={
                        "superseded_by": canonical.id,
                        "state": {"before": "active", "after": "archived"},
                    },
                )
                MEMORIES_DEDUPED.inc()
                merged_ids.append(memory.id)
            clusters.append(DedupCluster(canonical_id=canonical.id, merged_ids=merged_ids))

    db.commit()
    logger.info(
        "dedup_pass",
        extra={"namespace": namespace, "scanned": len(rows), "clusters": len(clusters)},
    )
    return clusters
