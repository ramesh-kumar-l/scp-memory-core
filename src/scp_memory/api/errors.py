"""Exception handlers that render the standard problem shape (10-api-contracts)."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from scp_memory.services.errors import NotFoundError, ServiceError

logger = logging.getLogger("scp_memory.api")


def _problem(status: int, code: str, message: str, details: dict | None = None) -> JSONResponse:
    body: dict = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return JSONResponse(status_code=status, content=body)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def _not_found(_request: Request, exc: NotFoundError) -> JSONResponse:
        return _problem(404, exc.code, str(exc))

    @app.exception_handler(ServiceError)
    async def _service_error(_request: Request, exc: ServiceError) -> JSONResponse:
        return _problem(400, exc.code, str(exc))
