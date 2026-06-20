# scp-memory-sdk (Python)

Official Python client for the **SCP Memory Engine**. Covers the full `v1`
surface: memory CRUD + audit, intelligence (decay / dedup / consolidate), hybrid
retrieval, and the trust layer.

## Install

```bash
pip install scp-memory-sdk        # from this monorepo: pip install ./sdks/python
```

Requires Python 3.11+ and `httpx`.

## Quickstart

```python
from scp_memory_sdk import SCPMemoryClient

with SCPMemoryClient("http://localhost:8000", actor="alice") as client:
    mem = client.memories.create(
        content="the user prefers dark mode",
        namespace="user:1",
        type="preference",
        source="settings",
    )

    # Hybrid retrieval — every result carries explainable signals + a trust verdict.
    hits = client.retrieval.search(query="what theme?", namespace="user:1")
    top = hits.results[0]
    print(top.score, top.signals.trust, top.trust.explanation)

    # Filter low-trust results.
    confident = client.retrieval.search(
        query="what theme?", namespace="user:1", min_confidence=0.7
    )

    # Standalone trust explanation.
    verdict = client.trust.explain(mem.id, namespace="user:1")
    print(verdict.confidence, verdict.explanation)
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

Non-2xx responses raise `ApiError` (or `NotFoundError` / `ValidationError`),
each exposing `.status`, `.code`, `.message`, and `.details`.

## Testing in-process

Inject a pre-built httpx client (e.g. FastAPI's `TestClient`) to exercise the SDK
against the app with no network or running server:

```python
from fastapi.testclient import TestClient
from scp_memory.api.app import create_app
from scp_memory_sdk import SCPMemoryClient

client = SCPMemoryClient(http_client=TestClient(create_app(init=False)), actor="alice")
```
