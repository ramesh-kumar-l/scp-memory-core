"""Phase 4 quickstart: trust signals on retrieval + the explain endpoint.

Runs against the in-process app via TestClient — no server or DB setup needed:

    python examples/trust_quickstart.py
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

    def add(content: str, source: str) -> dict:
        return client.post(
            "/v1/memories",
            json={"content": content, "namespace": ns, "type": "preference", "source": source},
            headers={"X-Actor": "demo"},
        ).json()

    # A user-stated preference, corroborated by a near-duplicate, plus a weak guess.
    pinned = add("the user prefers dark mode in the application", source="user")
    add("the user prefers dark mode across the whole application", source="user")
    add("the user might prefer a compact layout", source="inferred")

    print("=== retrieval with trust signals ===")
    resp = client.post(
        "/v1/retrieval/search",
        json={"query": "dark mode preference", "namespace": ns, "k": 5},
    )
    for r in resp.json()["results"]:
        t = r["trust"]
        print(f"\n[{r['score']:.3f}] {r['memory']['content']}")
        print(f"   signals: {r['signals']}")
        print(f"   trust  : {t['score']:.2f} — {t['explanation']}")

    print("\n=== filtering by confidence (min_confidence=0.9) ===")
    resp = client.post(
        "/v1/retrieval/search",
        json={"query": "layout preference", "namespace": ns, "min_confidence": 0.9},
    )
    print(f"results kept: {resp.json()['count']} (the inferred guess is filtered out)")

    print("\n=== standalone explain endpoint ===")
    resp = client.get(f"/v1/trust/{pinned['id']}", params={"namespace": ns})
    print(resp.json()["explanation"])


if __name__ == "__main__":
    main()
