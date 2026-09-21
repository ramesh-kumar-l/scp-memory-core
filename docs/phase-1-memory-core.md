# Phase 1 — Memory Core

Persistent, audited memory CRUD. This is the foundation every later phase builds
on (intelligence, retrieval, trust). Design intent lives in the
[memory bank](../project-memory-bank/README.md); this doc is the developer guide.

## What's implemented

- **Entities** (`src/scp_memory/models/`): `Memory`, `Provenance`, `AuditEvent`,
  `MemoryRelation` (table only, for Phase 2 graph edges).
- **Memory service** (`services/memory_service.py`): create / get / update /
  delete / list, all namespace-scoped.
- **Audit trail** (`services/audit_service.py`): append-only event on every
  mutation, written in the same transaction as the change.
- **API** (`api/routes/memories.py`): the Phase 1 surface from
  [10-api-contracts](../project-memory-bank/10-api-contracts.md).
- **Observability**: Prometheus metrics + JSON logs (no memory content logged).

## Run it

```bash
pip install -e ".[dev]"
python -m scp_memory            # serves on http://localhost:8000
# interactive docs at /docs ; metrics at /metrics
python examples/quickstart.py   # end-to-end demo, no server needed
```

Configuration is environment-driven (`SCP_` prefix), e.g.
`SCP_DATABASE_URL=postgresql+psycopg://…` to target Postgres instead of SQLite.

## API

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/memories` | Create a memory (→ 201) |
| GET | `/v1/memories/{id}` | Fetch a memory (touches `last_accessed_at`) |
| PATCH | `/v1/memories/{id}` | Partial update (content/type/metadata) |
| DELETE | `/v1/memories/{id}` | Governed delete (`?hard=true` to erase) |
| GET | `/v1/memories` | List/filter by `namespace`, `type`, `state`, paging |
| GET | `/v1/memories/{id}/audit` | Audit trail (survives hard delete) |
| GET | `/health`, `/metrics` | Liveness, Prometheus scrape |

- **Actor**: pass `X-Actor` header; recorded on provenance and every audit event.
- **Namespacing**: list requires `namespace`; per-id calls accept an optional
  `namespace` that scopes access — a mismatch returns 404 (no cross-tenant leak).
- **Errors**: standard problem shape `{"error": {"code", "message", "details?"}}`.

## Invariants (enforced + tested)

- Every mutation emits exactly one audit event, atomically.
- Provenance is always recorded on create.
- Soft-delete sets `state=deleted` and hides the memory from reads; the audit
  trail is retained. Hard-delete removes the row but keeps the audit trail.
- The relational record is the source of truth.

## Tests

```bash
pytest -m "not benchmark"   # unit + integration
pytest -m benchmark         # latency seed
```

## Not in Phase 1 (by design)

Importance/dedup/consolidation/decay (Phase 2), retrieval (Phase 3), trust
runtime (Phase 4). The `memory_relations` table and the full enum vocabulary are
present now so those phases extend rather than rewrite.
