# 11 — Data Models

**Status:** Design draft (Phase 0) · **Last updated:** 2026-06-20

> **Draft.** Persisted schema intent. Finalized as SQLAlchemy models in Phase 1.
> The relational store is the **source of truth**; the vector store (Qdrant) holds
> derived embeddings keyed by `memory_id`.

## Tables (relational — SQLite/Postgres)

### `memories`
| Column | Type | Notes |
|---|---|---|
| `id` | str (UUID) PK | server-generated |
| `content` | text | the memory payload |
| `type` | str | fact / event / preference / summary / … |
| `state` | str | active / consolidated / decayed / archived / deleted |
| `importance` | float null | derived (Phase 2) |
| `namespace` | str | tenant/owner scoping |
| `metadata` | json | arbitrary tags |
| `created_at` | datetime | |
| `updated_at` | datetime | |
| `last_accessed_at` | datetime null | updated on retrieval |

### `provenance`
| Column | Type | Notes |
|---|---|---|
| `memory_id` | str FK→memories.id | 1:1 |
| `source` | str | user / agent / document / system |
| `actor` | str | who/what created it |
| `derivation` | json | raw / summarized / consolidated_from[ids] |

### `audit_events` (append-only)
| Column | Type | Notes |
|---|---|---|
| `id` | str (UUID) PK | |
| `memory_id` | str FK | indexed |
| `action` | str | create / update / delete / consolidate / decay |
| `actor` | str | |
| `timestamp` | datetime | indexed |
| `diff` | json | before/after or change set |

### `memory_relations` (graph edges; mirrors NetworkX)
| Column | Type | Notes |
|---|---|---|
| `src_id` | str FK | |
| `dst_id` | str FK | |
| `relation` | str | derived_from / related_to / supersedes |

## Vector store (Qdrant)

Collection `memories` — points keyed by `memory_id`:
- `vector` (embedding), `model`, `dim`
- payload mirror of filterable metadata: `namespace`, `type`, `state`,
  `created_at` (for filtered ANN search).

## Indexing / Integrity

- Index `memories(namespace, state)`, `audit_events(memory_id, timestamp)`.
- Deletes are governed: soft-delete (`state=deleted`) + audit, with hard-delete
  available for compliance ([16-security-model](16-security-model.md)).
- Vector points are kept in sync with relational state (write-through in Phase 3).

## Related

[10-api-contracts](10-api-contracts.md) · [04-domain-model](04-domain-model.md) · [12-memory-model](12-memory-model.md) · [25-adr-log](25-adr-log.md)
