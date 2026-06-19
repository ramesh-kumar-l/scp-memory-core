# 10 — API Contracts

**Status:** Design draft (Phase 0) · **Last updated:** 2026-06-20

> **Draft.** This is design intent to align the team. Concrete endpoints land in
> Phase 1 (CRUD + audit) and Phase 3–4 (retrieval + trust). Shapes will be refined
> against Pydantic models when implemented.

## Conventions

- REST over HTTP/JSON; FastAPI + Pydantic.
- Versioned base path: `/v1`.
- IDs are server-generated strings (UUID). Timestamps ISO-8601 UTC.
- Errors: standard problem shape `{ "error": { "code", "message", "details" } }`.

## Phase 1 — Memory CRUD + Audit

```
POST   /v1/memories            Create a memory
GET    /v1/memories/{id}        Get a memory
PATCH  /v1/memories/{id}        Update a memory
DELETE /v1/memories/{id}        Delete (governed) a memory
GET    /v1/memories            List/filter memories (metadata, namespace, paging)
GET    /v1/memories/{id}/audit  Audit trail for a memory
```

Create (draft):
```json
POST /v1/memories
{ "content": "User prefers dark mode",
  "type": "preference",
  "metadata": { "namespace": "user:123", "source": "settings" } }
→ 201 { "id": "mem_...", "state": "active", "created_at": "..." }
```

## Phase 3 — Retrieval (added later)

```
POST   /v1/retrieve            Hybrid retrieval (keyword + vector + metadata)
```
```json
POST /v1/retrieve
{ "query": "what theme does the user like?",
  "filters": { "namespace": "user:123" },
  "k": 5, "mode": "hybrid" }
→ 200 { "results": [ { "memory_id": "...", "score": 0.82,
        "signals": { "keyword": 0.3, "vector": 0.78, "metadata": 1.0 } } ] }
```

## Phase 4 — Trust (added later)

Retrieval results gain `trust`: `{ provenance_quality, confidence, freshness,
explanation }`. An explain endpoint may be exposed:
```
GET    /v1/retrieve/{result_id}/explain
```

## Cross-Cutting

- AuthN/Z and namespacing per [16-security-model](16-security-model.md).
- Every mutating call emits an AuditEvent.
- All responses are explainable where relevant (signals travel with results).

## Related

[11-data-models](11-data-models.md) · [04-domain-model](04-domain-model.md) · [13-retrieval-model](13-retrieval-model.md) · [15-trust-model](15-trust-model.md)
