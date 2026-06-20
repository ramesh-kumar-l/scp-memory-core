"""Structured JSON logs carry extras + trace fields, never content (Phase 6)."""

import json
import logging

from scp_memory.logging_config import JsonFormatter


def _record(msg: str = "memory created") -> logging.LogRecord:
    return logging.LogRecord("scp_memory", logging.INFO, __file__, 1, msg, (), None)


def test_formatter_emits_valid_json_with_promoted_extras():
    record = _record()
    record.memory_id = "mem_123"
    record.actor = "alice"

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["message"] == "memory created"
    assert payload["memory_id"] == "mem_123"
    assert payload["actor"] == "alice"


def test_no_trace_ids_without_active_span():
    """Outside a traced request there is no span, so no trace_id leaks in."""
    payload = json.loads(JsonFormatter().format(_record()))
    assert "trace_id" not in payload
    assert "span_id" not in payload
