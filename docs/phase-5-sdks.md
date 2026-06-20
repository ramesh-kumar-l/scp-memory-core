# Phase 5 — SDKs (Python + TypeScript)

Official client libraries that expose the **full `v1` surface** — memory CRUD +
audit, intelligence (decay / dedup / consolidate), hybrid retrieval, and the
trust layer — so applications integrate without hand-rolling HTTP.

Both SDKs are thin, typed, and 1:1 with the API schemas
(`src/scp_memory/schemas`). They add no behaviour the server doesn't have; they
map requests/responses to native types and translate the error envelope to typed
exceptions.

## Layout

```
sdks/
  python/      scp-memory-sdk  (httpx, sync)
    src/scp_memory_sdk/{client,_http,errors,models}.py + resources/
  typescript/  @scp/memory-sdk (Fetch API, Node 18+/browser/Deno)
    src/{client,http,errors,types}.ts + resources/
```

Each resource module maps to one API router (`memories`, `intelligence`,
`retrieval`, `trust`). Every file is < 300 lines (strict modularity).

## Surface (both SDKs)

| Group | Methods | Endpoint |
|---|---|---|
| `memories` | `create`, `get`, `update`, `delete`, `list`, `audit` | `/v1/memories…` |
| `intelligence` | `decay`, `dedup`, `consolidate` | `/v1/intelligence/…` |
| `retrieval` | `search` | `/v1/retrieval/search` |
| `trust` | `explain` | `/v1/trust/{id}` |
| client | `health` | `/health` |

Search results carry the full explainability contract — per-signal scores
(`keyword`/`vector`/`metadata`/`importance`/`trust`), the fusion `weights`, and a
decomposable `trust` breakdown with a plain-language `explanation`.

## Design decisions

- **Transport seam.** Python wraps `httpx` (sync); a pre-built client can be
  injected (`http_client=`) so tests run in-process against FastAPI's `TestClient`
  with no network. TypeScript uses the global `fetch`; a `fetchFn` can be injected
  for tests/runtimes without a global fetch.
- **Audit identity.** Both send the caller's `X-Actor` header (mutations are
  audited server-side).
- **Errors.** `ApiError` with `NotFoundError` (404) and `ValidationError`
  (400/422) subclasses, each exposing `status` / `code` / `message` / `details`.
- **Forward-compatible parsing.** Unknown response keys are ignored, so a newer
  server stays compatible with an older client. Timestamps stay ISO-8601 strings.
- **Versioning.** Both pinned at `0.5.0`, tracking the engine.

## Verify

- **Python:** `pytest tests/integration/test_python_sdk.py` — full round trip
  (CRUD → audit → retrieval-with-trust → trust explain → consolidate) against the
  live app in-process.
- **TypeScript:** `cd sdks/typescript && npm install && npm run typecheck && npm test`
  — strict `tsc` + vitest over a stubbed fetch (request shape, parsing, error mapping).
- **Example:** `python examples/sdk_quickstart.py`.

## Deferred

- Async Python client and streaming; auto-generated API reference; publishing to
  PyPI / npm (packaging is ready: `hatchling` wheel + `tsc` build).
