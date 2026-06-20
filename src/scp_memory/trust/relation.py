"""Pairwise memory relation — pure (15-trust-model).

Confidence rises with corroboration (independent memories that agree) and falls
with contradiction. Deciding whether two memories *agree*, *conflict*, or are
*unrelated* is the swappable heart of that signal: the lexical detector here is
the hermetic, zero-infra default; a semantic NLI detector (``SCP_TRUST_NLI``)
slots in behind the same ``Relation`` contract without changing trust scoring.

This module holds only the lexical decision — token-overlap for topicality and
negation-polarity divergence for conflict — kept pure so it is exhaustively
unit-testable and reused by the detector seam (``services.relation_detector``).
"""

from enum import Enum

from scp_memory.intelligence.similarity import jaccard

# Lexical negation markers — a divergence in polarity between two otherwise highly
# similar memories signals contradiction (stand-in for real NLI).
NEGATIONS: frozenset[str] = frozenset(
    {"not", "no", "never", "none", "dont", "doesnt", "cant", "cannot", "wont", "isnt", "arent"}
)


class Relation(Enum):
    """How two memories relate for the purposes of trust corroboration."""

    NEUTRAL = "neutral"  # unrelated / not about the same thing
    AGREE = "agree"  # corroborating
    CONFLICT = "conflict"  # contradicting


def lexical_relation(
    a_tokens: set[str],
    b_tokens: set[str],
    *,
    threshold: float,
    negations: frozenset[str] = NEGATIONS,
) -> Relation:
    """Decide the relation between two token sets.

    Below the overlap ``threshold`` the memories are not about the same thing
    (``NEUTRAL``). At/above it, matching negation polarity corroborates
    (``AGREE``); divergent polarity — one negates, the other does not — flips
    agreement into ``CONFLICT``.
    """
    if jaccard(a_tokens, b_tokens) < threshold:
        return Relation.NEUTRAL
    a_neg = bool(a_tokens & negations)
    b_neg = bool(b_tokens & negations)
    if a_neg != b_neg:
        return Relation.CONFLICT
    return Relation.AGREE
