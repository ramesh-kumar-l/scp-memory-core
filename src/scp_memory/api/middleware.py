"""Request middleware: correlation IDs and latency metrics (17-observability-model)."""

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from scp_memory.metrics import API_REQUEST_DURATION


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Attach a request ID and record per-endpoint latency histograms."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start

        route = request.scope.get("route")
        endpoint = getattr(route, "path", request.url.path)
        API_REQUEST_DURATION.labels(
            method=request.method,
            endpoint=endpoint,
            status=str(response.status_code),
        ).observe(elapsed)
        response.headers["X-Request-ID"] = request_id
        return response
