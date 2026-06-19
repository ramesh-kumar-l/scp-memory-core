"""Phase 2 quickstart: importance, deduplication, consolidation, decay.

Runs against the in-process app via TestClient — no server or DB setup needed:

    python examples/intelligence_quickstart.py

HTTP equivalents (against `python -m scp_memory` on :8000) are shown in comments.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fastapi.testclient import TestClient  # noqa: E402

from scp_memory.api.app import create_app  # noqa: E402


def main() -> None:
    client = TestClient(create_app(init=False))
    from scp_memory.db.session import init_db

    init_db()
    ns = "user:demo"
    actor = {"X-Actor": "intel-demo"}

    def add(content: str) -> dict:
        return client.post(
            "/v1/memories", json={"content": content, "namespace": ns}, headers=actor
        ).json()

    # Every memory carries a derived importance score in [0, 1].
    m = add("User signed up for the pro plan")
    print("importance at create:", m["importance"], "access_count:", m["access_count"])

    # Two near-identical memories → deduplication keeps one canonical, archives the other.
    add("User prefers concise answers")
    add("User prefers concise answers")
    # curl -X POST :8000/v1/intelligence/dedup -d '{"namespace":"user:demo"}'
    dedup = client.post("/v1/intelligence/dedup", json={"namespace": ns}).json()
    print("dedup merged_count:", dedup["merged_count"])

    # Consolidate two related memories into a single summary memory.
    a = add("User enabled two-factor auth")
    b = add("User added a recovery email")
    # curl -X POST :8000/v1/intelligence/consolidate \
    #   -d '{"namespace":"user:demo","source_ids":[a,b]}'
    consolidated = client.post(
        "/v1/intelligence/consolidate",
        json={"namespace": ns, "source_ids": [a["id"], b["id"]]},
        headers=actor,
    ).json()
    print("summary memory:", consolidated["summary"]["id"], consolidated["summary"]["type"])

    # Decay recomputes importance and ages out stale, low-value memories.
    # curl -X POST :8000/v1/intelligence/decay -d '{"namespace":"user:demo"}'
    decay = client.post("/v1/intelligence/decay", json={"namespace": ns}).json()
    print("decay scanned:", decay["scanned"], "decayed:", decay["decayed"])

    # The default listing shows only live (active) memories.
    listing = client.get("/v1/memories", params={"namespace": ns}).json()
    print("active memories:", listing["total"])


if __name__ == "__main__":
    main()
