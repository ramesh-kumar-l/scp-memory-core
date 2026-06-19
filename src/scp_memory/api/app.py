"""FastAPI application factory (03-system-architecture: API Layer)."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from scp_memory.api.errors import register_error_handlers
from scp_memory.api.middleware import ObservabilityMiddleware
from scp_memory.api.routes import health, intelligence, memories
from scp_memory.config import get_settings
from scp_memory.logging_config import configure_logging


def create_app(*, init: bool = True) -> FastAPI:
    """Build the FastAPI app.

    Args:
        init: create the schema on the process-wide engine at startup. Tests pass
            ``init=False`` and override the DB dependency with an isolated engine.
    """
    settings = get_settings()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        if init:
            from scp_memory.db.session import init_db

            init_db()
        yield

    app = FastAPI(
        title="SCP Memory Engine — Memory Core",
        version="0.2.0",
        summary="Audited memory CRUD + self-management: importance, dedup, "
        "consolidation, decay (Phase 2).",
        lifespan=lifespan,
    )
    app.add_middleware(ObservabilityMiddleware)
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(memories.router)
    app.include_router(intelligence.router)
    return app
