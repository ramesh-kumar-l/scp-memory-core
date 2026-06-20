"""Structured JSON logging (17-observability-model).

Logs carry IDs and metadata only — never memory *content* (privacy). When the
optional tracing stack is active (``[observability]`` extra + a current span),
each record is stamped with the OpenTelemetry ``trace_id`` / ``span_id`` so logs
correlate with traces in Grafana. The import is guarded, so logging works
unchanged when OpenTelemetry is not installed.
"""

import json
import logging
from datetime import UTC, datetime

try:  # tracing is optional — correlate logs with traces only when available
    from opentelemetry.trace import get_current_span
except ImportError:  # pragma: no cover - exercised only without the extra
    get_current_span = None


def _trace_ids() -> dict[str, str]:
    """Current trace/span IDs as zero-padded hex, or empty when not tracing."""
    if get_current_span is None:
        return {}
    ctx = get_current_span().get_span_context()
    if not ctx.is_valid:
        return {}
    return {"trace_id": format(ctx.trace_id, "032x"), "span_id": format(ctx.span_id, "016x")}


class JsonFormatter(logging.Formatter):
    """Render log records as single-line JSON."""

    _RESERVED = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {
        "message",
        "asctime",
        "taskName",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        payload.update(_trace_ids())
        # Promote structured extras (e.g. memory_id, actor, request_id).
        for key, value in record.__dict__.items():
            if key not in self._RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    """Install the JSON formatter on the root logger (idempotent)."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
