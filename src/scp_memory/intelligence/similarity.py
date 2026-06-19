"""Text similarity — pure functions (12-memory-model: deduplication).

Phase 2 detects near-duplicates **lexically** (token-set Jaccard). This is a
deliberate interim: semantic (embedding-based) similarity arrives with the vector
store in Phase 3 ([13-retrieval-model]). The service layer can swap the scorer
without changing its merge logic.
"""

import re

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> set[str]:
    """Lowercase, split on non-alphanumeric, return the unique token set."""
    return set(_TOKEN_RE.findall(text.lower()))


def jaccard(a: set[str], b: set[str]) -> float:
    """|A ∩ B| / |A ∪ B|; 1.0 for identical token sets, 0.0 for disjoint."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0
