"""SDK exceptions mirroring the API error envelope (10-api-contracts).

The server renders errors as ``{"error": {"code", "message", "details"}}``. The
transport parses that envelope and raises the matching subclass so callers can
catch ``NotFoundError`` / ``ValidationError`` specifically, or ``ApiError`` for any
HTTP failure.
"""

from __future__ import annotations


class ApiError(Exception):
    """Any non-2xx response from the Memory Engine."""

    def __init__(
        self,
        status: int,
        code: str,
        message: str,
        details: dict | None = None,
    ) -> None:
        super().__init__(f"[{status} {code}] {message}")
        self.status = status
        self.code = code
        self.message = message
        self.details = details or {}


class NotFoundError(ApiError):
    """A resource (memory, namespace scope) was not found (HTTP 404)."""


class ValidationError(ApiError):
    """The request was rejected as invalid (HTTP 400 / 422)."""
