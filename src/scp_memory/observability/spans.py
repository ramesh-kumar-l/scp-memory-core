"""Manual tracing spans — no-op safe (17-observability-model, ADR-009/014).

Auto-instrumentation (tracing.py) traces the API and the database. This helper
adds *manual* spans around the retrieval pipeline's internal stages — candidate
fetch, vector search, keyword scoring, trust, fusion — so a slow query can be
attributed to a stage rather than a single opaque request span.

It is **no-op safe by construction**: if OpenTelemetry is not installed (the
default/offline path) or no tracer provider is configured (tracing disabled), the
context manager yields ``None`` and does nothing. No OpenTelemetry import happens
on the hot path until proven available, so the default install pays nothing.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

_OTEL_AVAILABLE: bool | None = None  # tri-state cache: None=unknown, False=absent, True=present


def _tracer() -> Any | None:
    """Return an OTel tracer if the SDK is importable, else ``None`` (cached)."""
    global _OTEL_AVAILABLE
    if _OTEL_AVAILABLE is False:
        return None
    try:
        from opentelemetry import trace
    except ImportError:
        _OTEL_AVAILABLE = False
        return None
    _OTEL_AVAILABLE = True
    # When tracing is disabled, this is the proxy/no-op tracer — start_span is cheap.
    return trace.get_tracer("scp_memory.retrieval")


@contextmanager
def span(name: str, **attributes: Any) -> Iterator[Any | None]:
    """Open a span ``name`` with ``attributes``; a no-op when tracing is unavailable."""
    tracer = _tracer()
    if tracer is None:
        yield None
        return
    with tracer.start_as_current_span(name) as current:
        for key, value in attributes.items():
            if value is not None:
                current.set_attribute(key, value)
        yield current
