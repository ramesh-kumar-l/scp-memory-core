"""Unit tests for the no-op-safe manual span helper."""

from scp_memory.observability.spans import span


def test_span_is_a_working_context_manager():
    # Whether or not OpenTelemetry is installed/configured, the span must yield
    # cleanly and never raise on the hot path.
    with span("test.stage", **{"scp.attr": "value"}) as s:
        result = 1 + 1
    assert result == 2
    # When OTel is absent or tracing disabled, the span is None (a true no-op).
    assert s is None or hasattr(s, "set_attribute")


def test_span_tolerates_none_attributes():
    with span("test.stage", **{"scp.maybe": None, "scp.count": 3}):
        pass  # must not raise even with a None-valued attribute
