# 16 — Security & Governance Model

**Status:** Design intent · **Last updated:** 2026-06-20

Memory is sensitive. Governance, audit, and privacy are part of the product, not
add-ons. Audit lands with Phase 1; richer controls layer in as phases progress.

## Threat Surface

- **Unauthorized access** to memories across namespaces/tenants.
- **Tampering** with memory content or audit records.
- **Leakage** of private memories via retrieval.
- **Untraceable changes** (who changed what, when).
- **Improper retention** (data kept beyond policy / privacy obligations).

## Controls

### Access & Isolation
- **Namespacing** scopes every memory to a tenant/owner; retrieval is always
  filtered by namespace ([13-retrieval-model](13-retrieval-model.md)).
- AuthN/Z at the API layer; authorization checked before any read/write.
- **Auth is enforced at the deployment proxy in front of engine + console
  (resolved 2026-06-20).** AuthN lives in infrastructure (reverse proxy /
  API gateway / SSO / mTLS) terminating the same-origin transport (ADR-015) for
  *both* the engine and the Admin Console. App code trusts the authenticated
  boundary; the Admin Console ships **no** bespoke login/session layer. Rationale:
  a console-only login is theater while `/v1/*` is directly reachable — one
  infra control point protects everything at near-zero app code and lower risk.
  Per-user authorization (RBAC over namespaces) is a separate, later **engine**
  concern, not a console one.

### Audit Trail (Phase 1)
- **Append-only** `audit_events` for every mutation (create/update/delete/
  consolidate/decay): actor, action, timestamp, diff.
- Audit is retained even when a memory is deleted.

### Data Lifecycle & Privacy
- **Governed deletion:** soft-delete by default (`state=deleted` + audit);
  **hard-delete** available for compliance (e.g., GDPR/erasure requests).
- Lifecycle **policies** (Phase 2+): e.g., "decay/forget low-importance memories
  older than N days" — policy actions are themselves audited.

### Integrity
- Relational store is the source of truth; vector points are derived and
  reconcilable.
- Provenance is preserved through consolidation.

## Explainability ⇄ Trust

Governance pairs with the trust model ([15-trust-model](15-trust-model.md)):
provenance and audit make trust scores defensible and decisions reviewable.

## Secrets & Deployment

- No secrets in the repo; configuration via environment.
- Local/on-device mode keeps all data on the device by default (local-first).

## Phase Notes

- Phase 1: audit trail + governed delete + namespacing.
- Later: policy engine, fine-grained authz, encryption-at-rest options.

## Related

[11-data-models](11-data-models.md) · [15-trust-model](15-trust-model.md) · [17-observability-model](17-observability-model.md) · [24-known-risks](24-known-risks.md)
