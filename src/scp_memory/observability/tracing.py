"""OpenTelemetry tracing wiring (17-observability-model, ADR-009/014).

Tracing is **opt-in** (``SCP_TRACING_ENABLED``) and disabled by default, so the
test suite and the offline dev path need no OpenTelemetry install. When enabled,
spans cover the full request path — API → service → store — via FastAPI and
SQLAlchemy auto-instrumentation, exported over OTLP to a collector (then Tempo).

Vendor-neutral by ADR-009: only OTLP is assumed, so the backend is swappable.
An explicit enable without the ``[observability]`` extra installed **fails
loudly** (mirrors the ADR-011 embedder contract — no silent degradation).
"""

import logging

from fastapi import FastAPI

from scp_memory.config import Settings, get_settings

logger = logging.getLogger("scp_memory.observability")

_INSTRUMENTED = False


def configure_tracing(app: FastAPI, *, settings: Settings | None = None) -> bool:
    """Wire OpenTelemetry tracing onto ``app`` if enabled.

    Returns ``True`` when tracing was configured, ``False`` when it is disabled
    (the default). Idempotent: instrumenting more than once is a no-op. Raises
    ``RuntimeError`` if tracing is enabled but the ``[observability]`` extra is
    not installed.
    """
    settings = settings or get_settings()
    if not settings.tracing_enabled:
        return False

    global _INSTRUMENTED
    if _INSTRUMENTED:
        return True

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError as exc:  # enabled but extra missing → fail loud
        raise RuntimeError(
            "SCP_TRACING_ENABLED is set but OpenTelemetry is not installed. "
            "Install the tracing dependencies: pip install 'scp-memory-core[observability]'."
        ) from exc

    resource = Resource.create({"service.name": settings.service_name})
    provider = TracerProvider(resource=resource)
    exporter = (
        OTLPSpanExporter(endpoint=settings.otlp_endpoint)
        if settings.otlp_endpoint
        else OTLPSpanExporter()  # honour standard OTEL_EXPORTER_OTLP_* env vars
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)
    # Instrument the process-wide engine so store spans nest under request spans.
    from scp_memory.db.session import engine

    SQLAlchemyInstrumentor().instrument(engine=engine)

    _INSTRUMENTED = True
    logger.info(
        "tracing configured",
        extra={"otlp_endpoint": settings.otlp_endpoint or "otel-sdk-default"},
    )
    return True
