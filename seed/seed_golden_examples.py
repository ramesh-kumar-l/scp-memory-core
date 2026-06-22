"""Seed the 10 Golden Examples into the SCP Memory Engine and verify them.

Single source of truth for the dataset is ``documents/golden-examples.json``; this
script loads it and creates each memory through the engine's HTTP API (the same
contract any client uses), then prints a verification summary.

Usage:
    # against a running engine (recommended — the console can then view it):
    python -m scp_memory                     # start the engine on :8000, then:
    python seed/seed_golden_examples.py
    python seed/seed_golden_examples.py --base-url http://localhost:8000

    # quick check with no server (in-process TestClient + SQLite file):
    python seed/seed_golden_examples.py --in-process

    # remove the seeded memories again:
    python seed/seed_golden_examples.py --reset

Notes:
    * The create API accepts content/namespace/type/metadata/source. It does NOT
      accept a client id, importance, backdated timestamps, or provenance
      derived_from — those are engine-owned. So on the engine the freshness/decay
      demo is muted (recorded_at = now). The Android seeder writes the Room DB
      directly and backdates ages, where decay is visible. This is intentional.
    * Zero third-party dependencies in HTTP mode (stdlib urllib only).
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "documents" / "golden-examples.json"
DEFAULT_BASE_URL = "http://localhost:8000"


# --------------------------------------------------------------------------- data
def load_dataset() -> dict:
    with DATASET.open(encoding="utf-8") as fh:
        return json.load(fh)


def create_payload(example: dict, namespace: str) -> dict:
    """Map a dataset entry to the engine's MemoryCreate contract."""
    return {
        "content": example["content"],
        "namespace": namespace,
        "type": example["type"],
        "metadata": example.get("metadata", {}),
        "source": example.get("provenance_source"),
    }


# ------------------------------------------------------------------------ transport
class Transport:
    """Minimal POST/GET/DELETE against the engine (HTTP or in-process)."""

    def post(self, path: str, body: dict, actor: str) -> tuple[int, dict]: ...
    def get(self, path: str) -> tuple[int, dict]: ...
    def delete(self, path: str, actor: str) -> int: ...


class HttpTransport(Transport):
    def __init__(self, base_url: str) -> None:
        self.base = base_url.rstrip("/")

    def _req(self, method: str, path: str, body: dict | None, actor: str | None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        if actor:
            req.add_header("X-Actor", actor)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw else {})
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            return exc.code, (json.loads(raw) if raw else {})

    def post(self, path, body, actor):
        return self._req("POST", path, body, actor)

    def get(self, path):
        return self._req("GET", path, None, None)

    def delete(self, path, actor):
        return self._req("DELETE", path, None, actor)[0]


class InProcessTransport(Transport):
    """TestClient over the in-process app (writes the engine's SQLite file)."""

    def __init__(self) -> None:
        sys.path.insert(0, str(ROOT / "src"))
        from fastapi.testclient import TestClient

        from scp_memory.api.app import create_app
        from scp_memory.db.session import init_db

        init_db()
        self._c = TestClient(create_app(init=False))

    def post(self, path, body, actor):
        r = self._c.post(path, json=body, headers={"X-Actor": actor})
        return r.status_code, (r.json() if r.content else {})

    def get(self, path):
        r = self._c.get(path)
        return r.status_code, (r.json() if r.content else {})

    def delete(self, path, actor):
        return self._c.delete(path, headers={"X-Actor": actor}).status_code


def make_transport(args) -> Transport:
    if args.in_process:
        return InProcessTransport()
    return HttpTransport(args.base_url)


# ----------------------------------------------------------------------- operations
def _preflight(t: Transport, base_hint: str) -> None:
    try:
        status, _ = t.get("/health")
    except urllib.error.URLError as exc:
        sys.exit(
            f"ERROR: cannot reach the engine at {base_hint} ({exc.reason}).\n"
            f"Start it first:  python -m scp_memory   (or use --in-process)"
        )
    if status != 200:
        sys.exit(f"ERROR: engine health check returned {status} at {base_hint}.")


def seed(t: Transport, data: dict) -> int:
    namespace, actor = data["namespace"], data["actor"]
    created = 0
    for ex in data["examples"]:
        status, body = t.post("/v1/memories", create_payload(ex, namespace), actor)
        if status in (200, 201):
            created += 1
            note = ex.get("demonstrates", "")
            print(f"  + {body.get('id', '?'):<28} {ex['type']:<11} {ex['id']}  - {note}")
        else:
            print(f"  ! FAILED {ex['id']} (HTTP {status}): {body}", file=sys.stderr)
    print(f"\nCreated {created}/{len(data['examples'])} memories in namespace '{namespace}'.")
    return created


def reset(t: Transport, data: dict) -> int:
    namespace, actor = data["namespace"], data["actor"]
    status, body = t.get(f"/v1/memories?namespace={namespace}&limit=200")
    if status != 200:
        sys.exit(f"ERROR: list failed (HTTP {status}): {body}")
    removed = 0
    for item in body.get("items", []):
        if t.delete(f"/v1/memories/{item['id']}?hard=true&namespace={namespace}", actor) == 204:
            removed += 1
    print(f"Removed {removed} memories from namespace '{namespace}'.")
    return removed


def verify(t: Transport, data: dict) -> None:
    namespace = data["namespace"]
    status, body = t.get(f"/v1/memories?namespace={namespace}&limit=200")
    total = body.get("total", 0) if status == 200 else 0
    print(f"\nVerify: GET /v1/memories?namespace={namespace} -> {total} items")

    # A trust-scored search that should rank the recent 'light mode' above 'dark mode'.
    status, body = t.post(
        "/v1/retrieval/search",
        {"query": "what theme does the user like?", "namespace": namespace, "k": 3},
        data["actor"],
    )
    if status == 200 and body.get("results"):
        # NB: on the hermetic engine path freshness is muted (recorded_at=now) and the
        # HashingEmbedder is a stand-in, so exact ordering is approximate; the trust
        # *scores* (provenance/confidence) are the reliable signal here. The freshness-
        # driven contradiction ranking is best seen on-device (backdated) or with real
        # embeddings (SCP_EMBEDDER=sentence-transformers).
        print("Verify: trust-scored search 'what theme does the user like?' ->")
        for r in body["results"]:
            trust = r.get("trust", {})
            conf = trust.get("confidence")
            conf_s = f"{conf:.2f}" if isinstance(conf, (int, float)) else "n/a"
            content = r.get("memory", {}).get("content", "")
            print(f"    score={r.get('score', 0):.2f}  trust.conf={conf_s}  {content[:60]}")
    else:
        print(f"Verify: retrieval check skipped (HTTP {status}).")
    print("\nOpen the Admin Console -> Memory Explorer (namespace 'demo:golden') to view them.")


# ------------------------------------------------------------------------------ main
def main() -> None:
    p = argparse.ArgumentParser(description="Seed/verify the 10 Golden Examples.")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Engine base URL.")
    p.add_argument("--in-process", action="store_true", help="Use an in-process TestClient (no server).")
    p.add_argument("--reset", action="store_true", help="Delete the seeded memories instead of creating them.")
    args = p.parse_args()

    data = load_dataset()
    t = make_transport(args)
    if not args.in_process:
        _preflight(t, args.base_url)

    if args.reset:
        reset(t, data)
        return

    seed(t, data)
    verify(t, data)


if __name__ == "__main__":
    main()
