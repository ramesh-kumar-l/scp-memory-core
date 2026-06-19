"""Quickstart: exercise the Memory Core API end-to-end.

Runs against the in-process app via FastAPI's TestClient, so it needs no running
server or database setup:

    python examples/quickstart.py

The equivalent HTTP calls (against `python -m scp_memory` on :8000) are shown in
comments next to each step.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fastapi.testclient import TestClient  # noqa: E402

from scp_memory.api.app import create_app  # noqa: E402


def main() -> None:
    client = TestClient(create_app(init=False))
    # The default app uses SQLite; here we let the app create its tables.
    from scp_memory.db.session import init_db

    init_db()

    actor = {"X-Actor": "quickstart"}

    # curl -X POST :8000/v1/memories -H 'X-Actor: quickstart' \
    #   -d '{"content":"User prefers dark mode","namespace":"user:123",
    #        "type":"preference","metadata":{"source":"settings"}}'
    created = client.post(
        "/v1/memories",
        json={
            "content": "User prefers dark mode",
            "namespace": "user:123",
            "type": "preference",
            "metadata": {"source": "settings"},
        },
        headers=actor,
    ).json()
    mem_id = created["id"]
    print("created:", mem_id, created["state"])

    # curl :8000/v1/memories/{id}
    print("get:", client.get(f"/v1/memories/{mem_id}").json()["content"])

    # curl -X PATCH :8000/v1/memories/{id} -d '{"content":"User prefers light mode"}'
    client.patch(
        f"/v1/memories/{mem_id}",
        json={"content": "User prefers light mode"},
        headers=actor,
    )

    # curl ':8000/v1/memories?namespace=user:123'
    listing = client.get("/v1/memories", params={"namespace": "user:123"}).json()
    print("list total:", listing["total"])

    # curl -X DELETE :8000/v1/memories/{id}
    client.delete(f"/v1/memories/{mem_id}", headers=actor)

    # curl :8000/v1/memories/{id}/audit
    audit = client.get(f"/v1/memories/{mem_id}/audit").json()
    print("audit actions:", [e["action"] for e in audit["items"]])


if __name__ == "__main__":
    main()
