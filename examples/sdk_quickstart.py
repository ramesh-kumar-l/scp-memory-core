"""Phase 5 quickstart: drive the engine through the official Python SDK.

Runs the SDK against the in-process app via TestClient — no server needed:

    python examples/sdk_quickstart.py
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "sdks" / "python" / "src"))

from fastapi.testclient import TestClient  # noqa: E402
from scp_memory_sdk import SCPMemoryClient  # noqa: E402

from scp_memory.api.app import create_app  # noqa: E402


def main() -> None:
    app = create_app(init=False)
    from scp_memory.db.session import init_db

    init_db()
    client = SCPMemoryClient(http_client=TestClient(app), actor="demo")
    ns = "user:demo"

    print("health:", client.health())

    client.memories.create(
        content="the user prefers dark mode in the application",
        namespace=ns,
        type="preference",
        source="user",
    )
    client.memories.create(
        content="the user prefers dark mode across the whole application",
        namespace=ns,
        type="preference",
        source="user",
    )
    guess = client.memories.create(
        content="the user might prefer a compact layout",
        namespace=ns,
        type="preference",
        source="inferred",
    )

    print("\n=== retrieval with trust signals ===")
    hits = client.retrieval.search(query="dark mode preference", namespace=ns, k=5)
    for r in hits.results:
        print(f"\n[{r.score:.3f}] {r.memory.content}")
        print(f"   trust: {r.trust.score:.2f} — {r.trust.explanation}")

    print("\n=== filter by confidence (min_confidence=0.9) ===")
    kept = client.retrieval.search(query="layout preference", namespace=ns, min_confidence=0.9)
    print(f"results kept: {kept.count} (the inferred guess is filtered out)")

    print("\n=== standalone trust explanation ===")
    verdict = client.trust.explain(guess.id, namespace=ns)
    print(f"confidence {verdict.confidence:.2f} — {verdict.explanation}")


if __name__ == "__main__":
    main()
