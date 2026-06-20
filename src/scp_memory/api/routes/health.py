"""Health/readiness probes and the Prometheus metrics endpoint (17-observability-model).

Two distinct probes for production orchestration (k8s-style):
- ``/health``       — *liveness*: the process is up. Never touches dependencies.
- ``/health/ready`` — *readiness*: dependencies (the DB) answer, so the instance
  can take traffic. Returns 503 when not ready so the orchestrator stops routing.
"""

import logging

from fastapi import APIRouter, Depends, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text
from sqlalchemy.orm import Session

from scp_memory.api.deps import get_db

router = APIRouter(tags=["ops"])
logger = logging.getLogger("scp_memory.api.health")


@router.get("/health")
def health() -> dict:
    """Liveness probe: the process is running (no dependency checks)."""
    return {"status": "ok"}


@router.get("/health/ready")
def ready(response: Response, db: Session = Depends(get_db)) -> dict:
    """Readiness probe: confirm the relational store answers a trivial query."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # dependency down → not ready, stop routing traffic
        logger.warning("readiness check failed", extra={"error": type(exc).__name__})
        response.status_code = 503
        return {"status": "not_ready", "database": "unavailable"}
    return {"status": "ready", "database": "ok"}


@router.get("/metrics")
def metrics() -> Response:
    """Prometheus scrape endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
