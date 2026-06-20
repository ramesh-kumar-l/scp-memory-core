"""Trust explainability (GET /v1/trust/{memory_id})."""

from __future__ import annotations

from scp_memory_sdk._http import HttpClient
from scp_memory_sdk.models import TrustBreakdown


class TrustResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def explain(self, memory_id: str, *, namespace: str) -> TrustBreakdown:
        """Return a memory's decomposable trust verdict + plain-language explanation."""
        return TrustBreakdown.from_dict(
            self._http.request("GET", f"/v1/trust/{memory_id}", params={"namespace": namespace})
        )
