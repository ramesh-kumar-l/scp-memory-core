# 29 — API Contracts (Consolidated, Implemented Surface)

**Status:** Implemented (Phases 1–6) · **Last updated:** 2026-06-20

> Authoritative, consolidated reference of the **engine HTTP surface as built**
> (supersedes the Phase-0 draft in [10-api-contracts](10-api-contracts.md) where
> they differ — e.g. retrieval is `POST /v1/retrieval/search`, not `/v1/retrieve`).
> Shapes below mirror the engine's Pydantic v2 models; fields marked *representative*
> reflect documented behaviour and may carry additional optional keys. This file is
> self-contained enough to drive a client (SDK or app) without reading source.

## Conventions

- REST over HTTP/JSON. Versioned base path: **`/v1`**.
- IDs are server-generated strings (UUID-like, prefixed e.g. `mem_…`). Timestamps
  are **ISO-8601 UTC**.
- **Namespace** scopes every memory (tenant/owner). It travels in the request body
  / query params, never inferred.
- **Same-origin transport, no CORS.** Clients call relative paths; a reverse proxy
  forwards `/v1`, `/health`, `/metrics` to the engine. (Native clients use an
  absolute base URL configured by the operator.)
- **Auth is enforced at the deployment proxy** (reverse proxy / API gateway / SSO /
  mTLS) in front of the engine — not in app code (see
  [16-security-model](16-security-model.md)). Clients should attach whatever
  credential the proxy expects (e.g. a bearer token / header) as opaque config.
- **Errors** use a standard problem shape:
  ```json
  { "error": { "code": "not_found", "message": "memory not found", "details": {} } }
  ```
  HTTP status codes: `200` ok · `201` created · `204` no content · `400` validation
  · `401/403` auth (from proxy) · `404` not found · `409` conflict · `422`
  unprocessable · `500` server.
- Every **mutating** call emits an append-only `AuditEvent` (actor, action,
  timestamp, diff).

## Endpoint Index

| Method | Path | Purpose | Phase |
|---|---|---|---|
| POST | `/v1/memories` | Create a memory | 1 |
| GET | `/v1/memories/{id}` | Get one memory | 1 |
| PATCH | `/v1/memories/{id}` | Update content/metadata | 1 |
| DELETE | `/v1/memories/{id}` | Governed delete (soft by default) | 1 |
| GET | `/v1/memories` | List/filter/page memories | 1 |
| GET | `/v1/memories/{id}/audit` | Audit trail for a memory | 1 |
| POST | `/v1/intelligence/dedup` | Run deduplication pass | 2 |
| POST | `/v1/intelligence/consolidate` | Run consolidation pass | 2 |
| POST | `/v1/intelligence/decay` | Run decay pass | 2 |
| POST | `/v1/retrieval/search` | Hybrid retrieval (keyword+vector+metadata+trust) | 3–4 |
| GET | `/v1/trust/{memory_id}` | Standalone trust breakdown | 4 |
| GET | `/health` | Liveness | 1 |
| GET | `/health/ready` | Readiness (DB/deps) | 6 |
| GET | `/metrics` | Prometheus exposition (text) | 6 |

---

## Memory Object (canonical shape)

```json
{
  "id": "mem_8f2a…",
  "namespace": "user:123",
  "type": "preference",            // fact | event | preference | summary
  "content": "User prefers dark mode",
  "state": "active",               // created | active | consolidated | decayed | archived | deleted
  "importance": 0.62,              // 0..1, scored by intelligence layer
  "access_count": 4,
  "metadata": { "source": "settings", "tags": ["ui"] },
  "provenance": {
    "source": "user",              // user | inferred | consolidation | system
    "derived_from": [],            // source memory ids for summaries
    "recorded_at": "2026-06-10T08:00:00Z"
  },
  "created_at": "2026-06-10T08:00:00Z",
  "updated_at": "2026-06-12T09:30:00Z",
  "last_accessed_at": "2026-06-18T14:02:00Z"
}
```

Field notes (*representative*): `importance`, `access_count`, `last_accessed_at`
are maintained by the engine (Phase 2) and are read-only to clients. `state`
transitions are driven by lifecycle ops, not direct writes.

---

## Phase 1 — Memory CRUD + Audit

### Create
```
POST /v1/memories
{
  "content": "User prefers dark mode",
  "type": "preference",
  "namespace": "user:123",
  "metadata": { "source": "settings" },
  "provenance": { "source": "user" }
}
→ 201  (full Memory object; state="active" after scoring)
```

### Get
```
GET /v1/memories/{id}
→ 200 Memory | 404
```

### Update
```
PATCH /v1/memories/{id}
{ "content": "User prefers dark mode at night", "metadata": { "tags": ["ui"] } }
→ 200 Memory   (emits AuditEvent with diff)
```

### Delete (governed)
```
DELETE /v1/memories/{id}              // soft-delete by default (state=deleted)
DELETE /v1/memories/{id}?hard=true    // compliance hard-delete (audit retained)
→ 204
```

### List / filter / page
```
GET /v1/memories?namespace=user:123&type=preference&state=active&limit=20&offset=0
→ 200
{
  "items": [ Memory, … ],
  "total": 137,
  "limit": 20,
  "offset": 0
}
```
Query params (*representative*): `namespace` (required for scoping), `type`,
`state`, `q` (optional substring), `limit`, `offset`.

### Audit trail
```
GET /v1/memories/{id}/audit
→ 200
{
  "items": [
    { "id": "evt_…", "action": "created", "actor": "user:123",
      "at": "2026-06-10T08:00:00Z", "diff": { … } },
    { "id": "evt_…", "action": "updated", "actor": "user:123",
      "at": "2026-06-12T09:30:00Z", "diff": { "content": ["old","new"] } }
  ]
}
```
Audit is **append-only** and retained even after delete.

---

## Phase 2 — Intelligence (lifecycle passes)

These run maintenance operations over a namespace and return a summary of what
changed. They are operator/demo actions, not per-request hot paths.

```
POST /v1/intelligence/dedup
{ "namespace": "user:123" }
→ 200 { "merged": 3, "archived_ids": ["mem_…"], "canonical_ids": ["mem_…"] }

POST /v1/intelligence/consolidate
{ "namespace": "user:123" }
→ 200 { "created_summaries": 1, "summary_ids": ["mem_…"], "derived_from": [["mem_…","mem_…"]] }

POST /v1/intelligence/decay
{ "namespace": "user:123" }
→ 200 { "decayed": 5, "decayed_ids": ["mem_…"] }
```
(*Response keys representative.*) Each transition emits an AuditEvent.

---

## Phase 3–4 — Hybrid Retrieval (with Trust)

The core demo endpoint. Metadata filter → (keyword ∪ vector) candidates → fuse →
rank → attach trust. Every result carries **per-signal scores** and a **trust
breakdown** (explainability is a contract guarantee, not optional).

### Request
```
POST /v1/retrieval/search
{
  "query": "what theme does the user like?",
  "namespace": "user:123",
  "filters": { "type": "preference", "state": "active" },
  "k": 5,
  "mode": "hybrid",                 // keyword | vector | hybrid  (default hybrid)
  "min_confidence": 0.0             // optional trust filter (0..1)
}
```

### Response
```json
{
  "query": "what theme does the user like?",
  "mode": "hybrid",
  "results": [
    {
      "memory_id": "mem_8f2a…",
      "content": "User prefers dark mode",
      "type": "preference",
      "score": 0.82,                       // fused final score
      "signals": {                         // per-signal contributions (explainability)
        "keyword": 0.30,
        "vector": 0.78,
        "metadata": 1.0,
        "importance": 0.62,
        "trust": 0.71
      },
      "weights": {                         // fusion weights in effect
        "keyword": 0.3, "vector": 0.3, "metadata": 0.1, "importance": 0.1, "trust": 0.2
      },
      "trust": {
        "provenance_quality": 0.9,
        "confidence": 0.75,
        "freshness": 0.6,
        "explanation": "User-stated preference (high provenance), corroborated by 2 memories, last confirmed 12 days ago."
      }
    }
  ]
}
```
Notes: `k` is bounded to protect latency. `signals`/`weights` keys present depend
on `mode`; in `keyword`/`vector` mode the unused candidate signal is `0`. Retrieval
**touches** returned items (updates `last_accessed_at`/`access_count`).

---

## Phase 4 — Standalone Trust

```
GET /v1/trust/{memory_id}
→ 200
{
  "memory_id": "mem_8f2a…",
  "provenance_quality": 0.9,
  "confidence": 0.75,
  "freshness": 0.6,
  "explanation": "User-stated preference (high provenance), corroborated by 2 memories, last confirmed 12 days ago.",
  "inputs": {                              // representative: decomposition for the UI
    "provenance_source": "user",
    "corroborations": 2,
    "contradictions": 0,
    "age_days": 12,
    "type_half_life_days": 180
  }
}
```
Trust scoring is **decomposable** (no black box):
- **provenance_quality** ← source mapping: `user`/explicit 1.0 → `consolidation` 0.75
  → `inferred` 0.5 → `system` 0.4 (unknown = 0.5 neutral).
- **confidence** = provenance floor, raised toward 1.0 by corroboration
  (saturating), reduced a fixed penalty per contradiction.
- **freshness** = type-aware exponential decay (`preference` ~180d half-life ≫
  `event` ~14d).
- Corroboration/contradiction are **lexical stand-ins** today (same-type neighbour
  token-overlap Jaccard ≥ 0.5, negation polarity). Swappable for NLI behind the
  same contract — **the response shape will not change**.

---

## Cross-Cutting / Ops

```
GET /health        → 200 { "status": "ok" }
GET /health/ready  → 200 { "status": "ready", "checks": { "db": "ok" } } | 503
GET /metrics       → 200 text/plain  (Prometheus exposition)
```
`/metrics` exposes counters (memory/retrieval/trust ops) and a request-latency
histogram. Clients that show SLIs parse this text client-side (no Grafana
dependency required).

## Stable-Contract Guarantees (for client authors)

1. Result objects **always** carry `signals` and `trust` — clients may render
   explainability unconditionally.
2. Trust response shape is **stable across the lexical→NLI swap**.
3. Namespacing is **mandatory**; never assume a global scope.
4. Soft-delete is default; deleted memories disappear from default retrieval but
   their audit persists.

## Related

[10-api-contracts](10-api-contracts.md) · [11-data-models](11-data-models.md) ·
[12-memory-model](12-memory-model.md) · [13-retrieval-model](13-retrieval-model.md) ·
[15-trust-model](15-trust-model.md) · [16-security-model](16-security-model.md)
