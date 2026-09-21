"""The SCP Memory Engine client — a facade over the four resource groups.

    from scp_memory_sdk import SCPMemoryClient

    with SCPMemoryClient("http://localhost:8000", actor="alice") as client:
        mem = client.memories.create(content="user prefers dark mode",
                                     namespace="user:1", type="preference",
                                     source="settings")
        hits = client.retrieval.search(query="theme?", namespace="user:1")
        verdict = client.trust.explain(mem.id, namespace="user:1")

Tests inject a pre-built ``httpx.Client`` (ASGI transport) via ``http_client`` to
exercise the SDK in-process with no network or running server.
"""

from __future__ import annotations

from typing import Any

import httpx

from scp_memory_sdk._http import DEFAULT_TIMEOUT, HttpClient
from scp_memory_sdk.resources import (
    IntelligenceResource,
    MemoriesResource,
    RetrievalResource,
    TrustResource,
)


class SCPMemoryClient:
    """Synchronous client covering the full v1 API surface."""

    def __init__(
        self,
        base_url: str | None = None,
        *,
        actor: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        transport: httpx.BaseTransport | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._http = HttpClient(
            base_url,
            actor=actor,
            timeout=timeout,
            transport=transport,
            client=http_client,
        )
        self.memories = MemoriesResource(self._http)
        self.intelligence = IntelligenceResource(self._http)
        self.retrieval = RetrievalResource(self._http)
        self.trust = TrustResource(self._http)

    def health(self) -> dict[str, Any]:
        """Liveness probe (GET /health)."""
        return self._http.request("GET", "/health")

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> SCPMemoryClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
