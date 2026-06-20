"""Tracing is opt-in and gated (Phase 6, ADR-014)."""

import importlib.util

import pytest
from fastapi import FastAPI

from scp_memory.config import Settings
from scp_memory.observability.tracing import configure_tracing


# The fail-loud path requires the *full* [observability] extra to be absent — the
# base opentelemetry API can be present transitively without the OTLP exporter /
# instrumentation packages the code actually imports.
def _installed(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except ModuleNotFoundError:  # a parent package is missing
        return False


_EXTRA_INSTALLED = all(
    _installed(mod)
    for mod in (
        "opentelemetry.exporter.otlp.proto.http.trace_exporter",
        "opentelemetry.instrumentation.fastapi",
        "opentelemetry.instrumentation.sqlalchemy",
    )
)


def test_tracing_disabled_by_default_is_noop():
    """The default path needs no OpenTelemetry install and configures nothing."""
    assert configure_tracing(FastAPI(), settings=Settings()) is False


@pytest.mark.skipif(_EXTRA_INSTALLED, reason="fail-loud path requires the extra to be absent")
def test_enabled_without_extra_fails_loud():
    """Explicit enable without the [observability] extra raises (no silent no-op)."""
    with pytest.raises(RuntimeError, match="observability"):
        configure_tracing(FastAPI(), settings=Settings(tracing_enabled=True))
