"""Importance service — applies scoring to a Memory and persists it.

Thin DB-aware wrapper over the pure functions in [intelligence.scoring]. It reads
the memory's age, access count, and explicit metadata signal, computes importance
in [0, 1], and writes it onto the row. Callers own the transaction (no commit).
"""

from datetime import datetime

from scp_memory.intelligence.scoring import ScoringConfig, explicit_score, score_importance
from scp_memory.models.memory import Memory
from scp_memory.utils.time import utcnow

# Process-wide default configuration. Kept here (not in Settings) so scoring stays
# a pure, self-contained concern; operational thresholds live in config.Settings.
_CONFIG = ScoringConfig()


def _age_seconds(created: datetime | None, now: datetime) -> float:
    """Robust age in seconds, tolerant of naive (SQLite) vs aware datetimes."""
    if created is None:
        return 0.0
    if created.tzinfo is None and now.tzinfo is not None:
        now = now.replace(tzinfo=None)
    elif created.tzinfo is not None and now.tzinfo is None:
        created = created.replace(tzinfo=None)
    return max(0.0, (now - created).total_seconds())


def recompute(memory: Memory, *, now: datetime | None = None) -> float:
    """Recompute and assign `memory.importance`; returns the new value."""
    now = now or utcnow()
    value = score_importance(
        age_seconds=_age_seconds(memory.created_at, now),
        access_count=memory.access_count or 0,
        explicit=explicit_score(memory.meta),
        config=_CONFIG,
    )
    memory.importance = value
    return value
