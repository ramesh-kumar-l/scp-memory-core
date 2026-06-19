"""Phase 3 quickstart: hybrid retrieval (keyword + vector + metadata + ranking).

Runs against the in-process app via TestClient — no server or DB setup needed:

    python examples/retrieval_quickstart.py

HTTP equivalent (against `python -m scp_memory` on :8000) is shown in comments.
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
    actor = {"X-Actor": "retrieval-demo"}

    def add(content: str) -> dict:
        return client.post(
            "/v1/memories", json={"content": content, "namespace": ns}, headers=actor
        ).json()

    add("The user prefers dark mode in the mobile app")
    add("The user's timezone is India Standard Time (IST)")
    add("The user upgraded to the pro subscription plan")
    add("Favourite cuisine is south indian breakfast")

    # Hybrid search fuses lexical (BM25) + vector + importance, and returns
    # explainable per-signal scores for every hit.
    # curl -X POST :8000/v1/retrieval/search \
    #   -d '{"query":"user prefers dark theme","namespace":"user:demo","k":3}'
    resp = client.post(
        "/v1/retrieval/search",
        json={"query": "user prefers dark theme", "namespace": ns, "k": 3},
    ).json()

    print(f"mode={resp['mode']} count={resp['count']}")
    for r in resp["results"]:
        print(f"  {r['score']:.3f}  {r['memory']['content']}")
        print(f"         signals={r['signals']}")

    # Keyword-only mode ignores the vector signal (precise on exact terms).
    kw = client.post(
        "/v1/retrieval/search",
        json={"query": "pro plan", "namespace": ns, "mode": "keyword"},
    ).json()
    print("\nkeyword-only top hit:", kw["results"][0]["memory"]["content"])


if __name__ == "__main__":
    main()
