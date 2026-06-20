# 08 — Active Phase

**Last updated:** 2026-06-20 · **Read this first, every session.**

> Doubles as the project's **active-context** save state (05 working agreement).

## Active Phase: 5 — SDKs ✅ complete (awaiting approval for Phase 6)

### Goal
Easy integration: official **Python** and **TypeScript** clients covering the
full `v1` surface (CRUD + audit, intelligence, hybrid retrieval, trust), so apps
never hand-roll HTTP. Plus the answer to the carried-over question — wire a real
**offline local embedding model** behind the existing `Embedder` seam.

### Deliverables
- [x] **Offline local embedder** (ADR-011): sentence-transformers
  `all-MiniLM-L6-v2`, opt-in via `SCP_EMBEDDER=sentence-transformers` + `[embeddings]`
  extra; `embedder_factory` selects it; hashing stays the hermetic default
- [x] **Python SDK** `scp-memory-sdk` (httpx, sync): full surface, typed models,
  typed errors, injectable client for in-process tests
- [x] **TypeScript SDK** `@scp/memory-sdk` (Fetch API): full surface, typed,
  injectable `fetchFn`, strict `tsc`
- [x] Tests: Python round-trip via `TestClient`; TS vitest over stubbed fetch
- [x] Docs (`docs/phase-5-sdks.md`), READMEs, `examples/sdk_quickstart.py`

### Exit Criteria (all met)
- **Published clients covering the full API incl. trust** — both SDKs expose every
  endpoint; search results carry the full trust breakdown.
- Python: 96 tests passing (+ benchmark); ruff + black clean. TS: 6 tests;
  `tsc --noEmit` + build clean.
- Strict modularity: longest new file 208 lines (SDK `models.py`; none > 300).
- Quality gates satisfied ([05-engineering-principles](05-engineering-principles.md)).

### Status
**Complete** (pending user confirmation). Awaiting approval to start Phase 6.

### Key decisions
- **Embedder is opt-in, not default.** Real semantic embeddings run **fully
  on-device** (no API calls); `embedding_offline=True` pins the loader to the local
  HF cache for air-gapped deploys. Explicit selection fails loudly if the model
  can't load (no silent degradation). Hashing stand-in remains the offline-by-default
  test path. NLI for trust stays deferred.
- **SDKs are thin and 1:1 with the API schemas** — no behaviour the server lacks.
  Transports are injectable (httpx client / `fetchFn`) so tests run in-process with
  no network. Errors map to `ApiError` / `NotFoundError` / `ValidationError`.
  Forward-compatible parsing (unknown keys ignored). Both pinned 0.5.0.
- Engine version unchanged (0.4.0); no DB migrations.

---

## ⛔ Stop Rule (operating model)

> One phase is active at a time. **Do NOT begin Phase 6 (Observability) without
> explicit user approval.** Never work ahead or skip phases.

At the end of any phase: update `07`, `08`, `28`, then **stop** and wait for
explicit instruction.

## Next Phase (do not start yet)

**Phase 6 — Observability:** Prometheus metrics + Grafana dashboards + OTel
tracing wiring + SLOs. Scoped in [09-backlog](09-backlog.md).

## Related

[07-current-state](07-current-state.md) · [28-session-handoff](28-session-handoff.md) · [23-roadmap](23-roadmap.md)
