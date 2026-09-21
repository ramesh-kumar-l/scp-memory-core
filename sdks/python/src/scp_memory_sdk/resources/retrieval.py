"""Hybrid retrieval (POST /v1/retrieval/search) — explainable, trust-aware."""

from __future__ import annotations

from scp_memory_sdk._http import HttpClient
from scp_memory_sdk.models import SearchResponse


class RetrievalResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def search(
        self,
        *,
        query: str,
        namespace: str,
        k: int = 10,
        mode: str = "hybrid",
        type: str | None = None,
        state: str | None = None,
        min_confidence: float | None = None,
    ) -> SearchResponse:
        """Run keyword+vector+metadata retrieval; each result carries trust signals."""
        body: dict = {"query": query, "namespace": namespace, "k": k, "mode": mode}
        if type is not None:
            body["type"] = type
        if state is not None:
            body["state"] = state
        if min_confidence is not None:
            body["min_confidence"] = min_confidence
        return SearchResponse.from_dict(
            self._http.request("POST", "/v1/retrieval/search", json=body)
        )
