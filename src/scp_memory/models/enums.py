"""Domain enums (04-domain-model, 12-memory-model).

Phase 1 exercises a subset of states (active / archived / deleted); the full set
is declared now for a stable vocabulary across phases.
"""

from enum import StrEnum


class MemoryType(StrEnum):
    fact = "fact"
    event = "event"
    preference = "preference"
    summary = "summary"
    other = "other"


class MemoryState(StrEnum):
    created = "created"
    active = "active"
    consolidated = "consolidated"  # Phase 2
    decayed = "decayed"  # Phase 2
    archived = "archived"
    deleted = "deleted"


class AuditAction(StrEnum):
    create = "create"
    update = "update"
    archive = "archive"
    restore = "restore"
    delete = "delete"
    consolidate = "consolidate"  # Phase 2
    decay = "decay"  # Phase 2


class RelationType(StrEnum):
    derived_from = "derived_from"
    related_to = "related_to"
    supersedes = "supersedes"
