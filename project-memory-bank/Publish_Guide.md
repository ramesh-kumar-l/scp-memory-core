# Publish Guide — SDKs (PyPI / npm) & Async Python Client

**Status:** practical runbook · **Last updated:** 2026-06-20

Per ADR-013 the SDKs stay in-repo until API freeze (1.0); this guide is the
step-by-step for *when* we publish, plus how to add the async Python client. It is
self-contained — follow it top to bottom.

Packages:

| Package | Location | Registry | Build |
|---|---|---|---|
| `scp-memory-sdk` (Python) | `sdks/python` | PyPI | hatchling wheel + sdist |
| `@scp/memory-sdk` (TypeScript) | `sdks/typescript` | npm | `tsc` → `dist/` |
| `scp-memory-core` (engine) | repo root | PyPI (optional) | hatchling |

---

## 0. Pre-flight (every release)

1. **Green gates:** `pytest -m "not benchmark" -q`, `ruff check`, `black --check`,
   and (TS) `npm run typecheck && npm run test`.
2. **Decide the version** (SemVer). Pre-1.0 the contract can still move; bump the
   **minor** for additive features, **patch** for fixes. Keep engine and SDK
   versions in lockstep at minor level (they share the API contract — see
   [29-api-contracts](29-api-contracts.md)).
3. **Changelog / release notes** — see [26-public-artifacts](26-public-artifacts.md).
4. **Tag after publish:** `git tag sdk-py-vX.Y.Z` (and `sdk-ts-…`), push tags.

> Publishing is **irreversible** — a version number can never be reused on PyPI or
> npm. Always dry-run to TestPyPI / `npm publish --dry-run` first.

---

## 1. Python SDK → PyPI

### 1.1 Bump the version
Edit `sdks/python/pyproject.toml` → `[project] version = "X.Y.Z"`. The version is
single-sourced there (hatchling reads it).

### 1.2 Build
```bash
cd sdks/python
python -m pip install --upgrade build twine
python -m build            # writes dist/scp_memory_sdk-X.Y.Z-py3-none-any.whl + .tar.gz
twine check dist/*         # validates metadata + long-description rendering
```

### 1.3 Dry-run to TestPyPI
```bash
twine upload --repository testpypi dist/*
# verify a clean install resolves and imports:
python -m venv /tmp/v && /tmp/v/bin/pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ scp-memory-sdk==X.Y.Z
/tmp/v/bin/python -c "import scp_memory_sdk; print(scp_memory_sdk.__name__)"
```

### 1.4 Publish to PyPI
**Preferred — Trusted Publishing (OIDC, no long-lived token).** Configure the
project on PyPI → *Publishing* → add a GitHub Actions publisher, then:
```yaml
# .github/workflows/release-sdk-python.yml
name: Publish Python SDK
on:
  push:
    tags: ["sdk-py-v*"]
jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write        # OIDC — required for trusted publishing
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install build && python -m build sdks/python
      - uses: pypa/gh-action-pypi-publish@release/v1
        with:
          packages-dir: sdks/python/dist
```
**Fallback — token:** `twine upload dist/*` with `TWINE_USERNAME=__token__` and
`TWINE_PASSWORD=<pypi-token>` (store as a CI secret; never commit — see
[16-security-model](16-security-model.md)).

### 1.5 Engine package (optional)
Same flow from the repo root (`python -m build`). Decide first whether the engine
ships as an installable library or only as the Docker image (`Dockerfile`).

---

## 2. TypeScript SDK → npm

### 2.1 Bump the version
```bash
cd sdks/typescript
npm version X.Y.Z --no-git-tag-version    # updates package.json + lockfile
```

### 2.2 Build & verify the publish surface
```bash
npm ci
npm run typecheck && npm run test
npm run build                  # emits dist/ (index.js + index.d.ts)
npm pack --dry-run             # lists the tarball; confirm only `dist` + `src` ship
```
`package.json` already declares `"files": ["dist","src"]`, `main`/`module`/`types`
→ `dist`, and `exports`. **`dist/` must be built before publish** (it is
git-ignored). For a public scoped package, `--access public` is required.

### 2.3 Dry-run, then publish
```bash
npm publish --dry-run --access public
npm publish --access public --provenance     # provenance needs CI OIDC (below)
```
CI variant:
```yaml
# .github/workflows/release-sdk-ts.yml
name: Publish TS SDK
on:
  push:
    tags: ["sdk-ts-v*"]
jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write          # provenance attestation
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20", registry-url: "https://registry.npmjs.org" }
      - run: npm ci && npm run build
        working-directory: sdks/typescript
      - run: npm publish --access public --provenance
        working-directory: sdks/typescript
        env: { NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }} }
```

---

## 3. Async Python client

The current `SCPMemoryClient` is synchronous (httpx sync). Async lets callers
`await` from FastAPI/asyncio without a threadpool. Mirror the existing facade so
both clients share resources and models.

### 3.1 Design (no contract change)
- Add `AsyncHttpClient` wrapping `httpx.AsyncClient` (mirror `_http.py`: base URL,
  `actor` header, timeout, error mapping in `errors.py`).
- Add async resource classes whose methods are `async def` and `await` the client.
  Keep request/response **models identical** — reuse `models.py` (pure Pydantic, no
  I/O), so only the transport differs.
- Add `AsyncSCPMemoryClient` with `async def close()` and
  `__aenter__/__aexit__`.

### 3.2 File layout
```
sdks/python/src/scp_memory_sdk/
  _http.py            # existing sync HttpClient
  _async_http.py      # new: AsyncHttpClient (httpx.AsyncClient)
  client.py           # existing SCPMemoryClient
  aio.py              # new: AsyncSCPMemoryClient + async resources
  resources/          # sync resources (unchanged)
```
Keep each file < 300 lines (strict modularity); if `aio.py` grows, split async
resources into `resources_async/`.

### 3.3 Usage
```python
from scp_memory_sdk.aio import AsyncSCPMemoryClient

async with AsyncSCPMemoryClient("http://localhost:8000", actor="alice") as client:
    mem = await client.memories.create(
        content="user prefers dark mode", namespace="user:1", type="preference"
    )
    hits = await client.retrieval.search(query="theme?", namespace="user:1")
```

### 3.4 Tests
Reuse the in-process pattern: inject an `httpx.AsyncClient` built on an
`ASGITransport` over the FastAPI app — no network, no running server (mirrors the
sync SDK's `http_client` injection). Mark with `pytest.mark.asyncio` (add
`pytest-asyncio` to the SDK `dev` extra).

### 3.5 Versioning
Adding the async client is **additive** → minor bump. Document it in the SDK
README and ship in the same release as the sync client.

---

## Related
[25-adr-log](25-adr-log.md) (ADR-013) · [20-release-plan](20-release-plan.md) ·
[26-public-artifacts](26-public-artifacts.md) · [29-api-contracts](29-api-contracts.md)
