"""Shared API schemas: the standard error envelope (10-api-contracts)."""

from pydantic import BaseModel


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody
