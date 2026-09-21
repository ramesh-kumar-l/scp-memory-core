"""Memory self-management passes (POST /v1/intelligence/{decay,dedup,consolidate})."""

from __future__ import annotations

from scp_memory_sdk._http import HttpClient
from scp_memory_sdk.models import ConsolidateResult, DecayResult, DedupResult


class IntelligenceResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def decay(self, *, namespace: str, threshold: float | None = None) -> DecayResult:
        body: dict = {"namespace": namespace}
        if threshold is not None:
            body["threshold"] = threshold
        return DecayResult.from_dict(
            self._http.request("POST", "/v1/intelligence/decay", json=body)
        )

    def dedup(self, *, namespace: str, threshold: float | None = None) -> DedupResult:
        body: dict = {"namespace": namespace}
        if threshold is not None:
            body["threshold"] = threshold
        return DedupResult.from_dict(
            self._http.request("POST", "/v1/intelligence/dedup", json=body)
        )

    def consolidate(
        self,
        *,
        namespace: str,
        source_ids: list[str],
        summary: str | None = None,
    ) -> ConsolidateResult:
        body: dict = {"namespace": namespace, "source_ids": source_ids}
        if summary is not None:
            body["summary"] = summary
        return ConsolidateResult.from_dict(
            self._http.request("POST", "/v1/intelligence/consolidate", json=body)
        )
