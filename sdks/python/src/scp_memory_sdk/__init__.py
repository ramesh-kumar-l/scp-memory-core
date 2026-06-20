"""Official Python SDK for the SCP Memory Engine (Phase 5).

Covers the full v1 surface: memory CRUD + audit, intelligence (decay/dedup/
consolidate), hybrid retrieval, and the trust layer.
"""

from scp_memory_sdk.client import SCPMemoryClient
from scp_memory_sdk.errors import ApiError, NotFoundError, ValidationError
from scp_memory_sdk.models import (
    AuditEvent,
    AuditLog,
    ConsolidateResult,
    DecayResult,
    DedupResult,
    Memory,
    MemoryPage,
    SearchResponse,
    SearchResult,
    SignalScores,
    TrustBreakdown,
)

__version__ = "0.5.0"
__all__ = [
    "SCPMemoryClient",
    "ApiError",
    "NotFoundError",
    "ValidationError",
    "Memory",
    "MemoryPage",
    "AuditEvent",
    "AuditLog",
    "SearchResponse",
    "SearchResult",
    "SignalScores",
    "TrustBreakdown",
    "DecayResult",
    "DedupResult",
    "ConsolidateResult",
]
