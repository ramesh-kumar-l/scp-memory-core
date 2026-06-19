"""Prometheus metrics (17-observability-model).

Every feature ships metrics (quality gate, 05-engineering-principles). Phase 6
consolidates these into dashboards; the instrumentation is added inline now.
"""

from prometheus_client import Counter, Histogram

MEMORIES_CREATED = Counter("scp_memories_created_total", "Memories created.")
MEMORIES_UPDATED = Counter("scp_memories_updated_total", "Memories updated.")
MEMORIES_DELETED = Counter("scp_memories_deleted_total", "Memories deleted.", ["mode"])
AUDIT_EVENTS = Counter("scp_audit_events_total", "Audit events recorded.", ["action"])
API_REQUEST_DURATION = Histogram(
    "scp_api_request_duration_seconds",
    "API request latency in seconds.",
    ["method", "endpoint", "status"],
)
