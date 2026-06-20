# @scp/memory-sdk (TypeScript)

Official TypeScript client for the **SCP Memory Engine**. Covers the full `v1`
surface: memory CRUD + audit, intelligence (decay / dedup / consolidate), hybrid
retrieval, and the trust layer. Uses the standard Fetch API — works in Node 18+,
browsers, and Deno.

## Install

```bash
npm install @scp/memory-sdk
```

## Quickstart

```ts
import { SCPMemoryClient } from "@scp/memory-sdk";

const client = new SCPMemoryClient({ baseUrl: "http://localhost:8000", actor: "alice" });

const mem = await client.memories.create({
  content: "the user prefers dark mode",
  namespace: "user:1",
  type: "preference",
  source: "settings",
});

// Hybrid retrieval — every result carries explainable signals + a trust verdict.
const hits = await client.retrieval.search({ query: "what theme?", namespace: "user:1" });
const top = hits.results[0];
console.log(top?.score, top?.signals.trust, top?.trust.explanation);

// Standalone trust explanation.
const verdict = await client.trust.explain(mem.id, "user:1");
console.log(verdict.confidence, verdict.explanation);
```

## Surface

| Group | Methods |
|---|---|
| `client.memories` | `create`, `get`, `update`, `delete`, `list`, `audit` |
| `client.intelligence` | `decay`, `dedup`, `consolidate` |
| `client.retrieval` | `search` |
| `client.trust` | `explain` |
| `client` | `health` |

## Errors

Non-2xx responses reject with `ApiError` (or `NotFoundError` / `ValidationError`),
each exposing `.status`, `.code`, `.message`, and `.details`.

## Develop

```bash
npm install
npm run typecheck   # tsc --noEmit
npm test            # vitest (fetch is stubbed; no server needed)
npm run build       # emit dist/
```

A custom `fetchFn` can be injected via the constructor for tests or non-global-fetch
runtimes.
