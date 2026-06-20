"""Thin synchronous HTTP transport over httpx.

Owns base URL, the ``X-Actor`` audit header, query-param cleanup, and translation
of the server error envelope into typed exceptions. Resource classes call
``request`` and never touch httpx directly. A pre-built ``httpx.Client`` can be
injected (e.g. an ASGI transport) for hermetic, in-process testing.
"""

from __future__ import annotations

from typing import Any

import httpx

from scp_memory_sdk.errors import ApiError, NotFoundError, ValidationError

DEFAULT_TIMEOUT = 30.0


def _clean(params: dict[str, Any] | None) -> dict[str, Any] | None:
    """Drop params whose value is ``None`` so they are omitted from the query."""
    if not params:
        return None
    return {k: v for k, v in params.items() if v is not None}


def _raise(response: httpx.Response) -> None:
    """Map an error response (problem envelope) to a typed exception."""
    code, message, details = "error", response.text, None
    try:
        body = response.json().get("error", {})
        code = body.get("code", code)
        message = body.get("message", message)
        details = body.get("details")
    except ValueError:
        pass
    status = response.status_code
    if status == 404:
        raise NotFoundError(status, code, message, details)
    if status in (400, 422):
        raise ValidationError(status, code, message, details)
    raise ApiError(status, code, message, details)


class HttpClient:
    """Synchronous transport. Use as a context manager to close owned clients."""

    def __init__(
        self,
        base_url: str | None = None,
        *,
        actor: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        transport: httpx.BaseTransport | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self._actor = actor
        if client is not None:
            self._client = client
            self._owns = False
        elif base_url is not None:
            self._client = httpx.Client(
                base_url=base_url.rstrip("/"), timeout=timeout, transport=transport
            )
            self._owns = True
        else:
            raise ValueError("either base_url or an httpx client must be provided")

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        """Send a request; return parsed JSON, or ``None`` for empty/204 responses."""
        headers = {"X-Actor": self._actor} if self._actor else {}
        response = self._client.request(
            method, path, params=_clean(params), json=json, headers=headers
        )
        if response.status_code >= 400:
            _raise(response)
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    def close(self) -> None:
        if self._owns:
            self._client.close()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
