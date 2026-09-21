"""Prometheus metrics (17-observability-model).

Every feature ships metrics (quality gate, 05-engineering-principles). Phase 6
consolidates these into dashboards; the instrumentation is added inline now.
"""

from prometheus_client import Counter, Histogram

MEMORIES_CREATED = Counter("scp_memories_created_total", "Memories created.")
MEMORIES_UPDATED = Counter("scp_memories_updated_total", "Memories updated.")
MEMORIES_DELETED = Counter("scp_memories_deleted_total", "Memories deleted.", ["mode"])
AUDIT_EVENTS = Counter("scp_audit_events_total", "Audit events recorded.", ["action"])
# Memory intelligence (Phase 2).
MEMORIES_DECAYED = Counter("scp_memories_decayed_total", "Memories transitioned to decayed.")
MEMORIES_DEDUPED = Counter("scp_memories_deduped_total", "Duplicate memories merged/archived.")
MEMORIES_CONSOLIDATED = Counter(
    "scp_memories_consolidated_total", "Summary memories produced by consolidation."
)
# Hybrid retrieval (Phase 3).
RETRIEVAL_QUERIES = Counter("scp_retrieval_queries_total", "Retrieval queries served.", ["mode"])
# Trust layer (Phase 4).
TRUST_EVALUATIONS = Counter("scp_trust_evaluations_total", "Standalone trust explanations served.")
API_REQUEST_DURATION = Histogram(
    "scp_api_request_duration_seconds",
    "API request latency in seconds.",
    ["method", "endpoint", "status"],
)
