# 28 — Session Handoff

**Last updated:** 2026-06-20 · **Read this first, every session.**

## Last Session Summary

**Date:** 2026-06-20
**Goal:** Answer the carried-over embedding question (offline local model), then
implement Phase 5 — SDKs (Python + TypeScript) over the full API incl. trust.

### What was done
- **Offline local embedder (ADR-011):** `retrieval/local_embedder.py`
  (`SentenceTransformerEmbedder`, lazy import, `all-MiniLM-L6-v2`, 384-dim, fully
  on-device; `HF_HUB_OFFLINE` pin for air-gap) + `retrieval/embedder_factory.py`
  (`build_embedder` selects via `SCP_EMBEDDER`). `config.Settings` gained
  `embedder` / `embedding_model` / `embedding_offline`. `retrieval_service` now
  builds its embedder via the factory — **default stays `HashingEmbedder`** so CI
  is offline-by-default. New `[embeddings]` extra. Verified: the real model loads
  and produces normalized 384-dim vectors.
- **Python SDK** (`sdks/python`, `scp-memory-sdk` 0.5.0, httpx sync): `client.py`
  facade + `resources/{memories,intelligence,retrieval,trust}.py` + typed `models.py`
  + `_http.py` (actor header, param cleanup, error mapping) + `errors.py`. Accepts
  an injected httpx client for in-process testing.
- **TypeScript SDK** (`sdks/typescript`, `@scp/memory-sdk` 0.5.0, Fetch API):
  `client.ts` + `resources/*.ts` + `types.ts` + `http.ts` + `errors.ts` + `index.ts`.
  Injectable `fetchFn`. Strict `tsconfig`.
- **Tests:** Python **96 passing** (+4 embedder-factory, +6 SDK round-trip via
  `TestClient`: CRUD/audit/retrieval-with-trust/min_confidence/trust/consolidate).
  TypeScript **6 passing** (vitest over stubbed fetch) + `tsc --noEmit` + build clean.
- **Docs/examples:** `docs/phase-5-sdks.md`, both SDK READMEs, `examples/sdk_quickstart.py`
  (verified end-to-end), ADR-011 + ADR-012 in `25-adr-log.md`.

### Decisions / notes
- Embedder is **opt-in, not default**; explicit selection **fails loudly** if the
  model can't load (no silent degradation). NLI for trust still deferred.
- SDKs are **thin, typed, 1:1 with the API schemas**; transports injectable so
  tests need no network/server; typed error hierarchy; forward-compatible parsing.
- Engine version unchanged (**0.4.0**); SDKs **0.5.0**. No DB migrations.

### State
- Phase 5 **complete**, pending confirmation. No commit made yet (Phases 1–5 all
  uncommitted on `master`).

## Where to Resume

**Next:** Phase 6 — Observability (Prometheus metrics + Grafana dashboards + OTel
tracing wiring + SLOs). See [09-backlog](09-backlog.md) Phase 6 section.

> **Do not start Phase 6 without explicit approval** ([08-active-phase](08-active-phase.md)).

## First Actions Next Session
1. Read `07`, `08`, `28` (this file).
2. Confirm Phase 5 acceptance / get approval to begin Phase 6.
3. If approved, follow the Phase 6 backlog with all quality gates.

## Open Questions for User
- Approve Phase 5 and authorize Phase 6?
- Commit the Phases 1–5 code now? (nothing has been committed yet)
- Publish the SDKs to PyPI / npm this cycle, or keep them in-repo for now?
- Should the production deployment default to `SCP_EMBEDDER=sentence-transformers`,
  and should trust adopt a real NLI model for corroboration/contradiction?

## Related

[07-current-state](07-current-state.md) · [08-active-phase](08-active-phase.md) · [09-backlog](09-backlog.md)
