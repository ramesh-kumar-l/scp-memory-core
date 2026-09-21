"""Memory CRUD + audit (POST/GET/PATCH/DELETE /v1/memories, .../audit)."""

from __future__ import annotations

from scp_memory_sdk._http import HttpClient
from scp_memory_sdk.models import AuditLog, Memory, MemoryPage


class MemoriesResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        content: str,
        namespace: str,
        type: str = "fact",
        metadata: dict | None = None,
        source: str | None = None,
    ) -> Memory:
        """Create a memory (emits an audit event server-side)."""
        body: dict = {"content": content, "namespace": namespace, "type": type}
        if metadata is not None:
            body["metadata"] = metadata
        if source is not None:
            body["source"] = source
        return Memory.from_dict(self._http.request("POST", "/v1/memories", json=body))

    def get(self, memory_id: str, *, namespace: str | None = None) -> Memory:
        return Memory.from_dict(
            self._http.request("GET", f"/v1/memories/{memory_id}", params={"namespace": namespace})
        )

    def update(
        self,
        memory_id: str,
        *,
        content: str | None = None,
        type: str | None = None,
        metadata: dict | None = None,
        namespace: str | None = None,
    ) -> Memory:
        body: dict = {}
        if content is not None:
            body["content"] = content
        if type is not None:
            body["type"] = type
        if metadata is not None:
            body["metadata"] = metadata
        return Memory.from_dict(
            self._http.request(
                "PATCH",
                f"/v1/memories/{memory_id}",
                params={"namespace": namespace},
                json=body,
            )
        )

    def delete(self, memory_id: str, *, hard: bool = False, namespace: str | None = None) -> None:
        self._http.request(
            "DELETE",
            f"/v1/memories/{memory_id}",
            params={"hard": hard, "namespace": namespace},
        )

    def list(
        self,
        *,
        namespace: str,
        type: str | None = None,
        state: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> MemoryPage:
        return MemoryPage.from_dict(
            self._http.request(
                "GET",
                "/v1/memories",
                params={
                    "namespace": namespace,
                    "type": type,
                    "state": state,
                    "limit": limit,
                    "offset": offset,
                },
            )
        )

    def audit(self, memory_id: str) -> AuditLog:
        return AuditLog.from_dict(self._http.request("GET", f"/v1/memories/{memory_id}/audit"))
