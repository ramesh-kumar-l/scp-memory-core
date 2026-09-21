"""Corroboration/contradiction detection seam (15-trust-model, R3).

Trust confidence depends on whether namespace neighbours *agree* or *conflict*
with a memory. Two detectors sit behind one ``Relation`` contract:

- ``LexicalRelationDetector`` (default) — token-overlap topicality + negation
  polarity. Hermetic, zero-infra, deterministic; the tested default path.
- ``NliRelationDetector`` (opt-in, ``SCP_TRUST_NLI=true``) — a local cross-encoder
  natural-language-inference model classifies each candidate pair as
  entailment / contradiction / neutral. Runs fully on-device; loaded lazily only
  when enabled so the default path never imports it. Fails loud if the
  ``[embeddings]`` extra is absent (mirrors the ADR-011 embedder contract).

The swap changes *how* agreement is judged, never the trust response shape — see
the calibration harness (``eval/run_trust_calibration.py``) for deciding when the
NLI path actually beats lexical before turning it on.
"""

import logging
from functools import lru_cache
from typing import Protocol

from scp_memory.config import get_settings
from scp_memory.models.memory import Memory
from scp_memory.trust.config import TrustConfig
from scp_memory.trust.relation import Relation, lexical_relation

logger = logging.getLogger("scp_memory.trust.relation")


class RelationDetector(Protocol):
    """Judges how a memory relates to a same-type neighbour."""

    name: str

    def relate(
        self,
        a: Memory,
        b: Memory,
        a_tokens: set[str],
        b_tokens: set[str],
        *,
        config: TrustConfig,
    ) -> Relation: ...


class LexicalRelationDetector:
    """Token-overlap + negation polarity (the hermetic default)."""

    name = "lexical"

    def relate(
        self,
        a: Memory,
        b: Memory,
        a_tokens: set[str],
        b_tokens: set[str],
        *,
        config: TrustConfig,
    ) -> Relation:
        return lexical_relation(a_tokens, b_tokens, threshold=config.corroboration_threshold)


class NliRelationDetector:  # pragma: no cover - integration-only (needs a model)
    """Local cross-encoder NLI: entailment→agree, contradiction→conflict.

    Threshold-gated so low-confidence predictions fall back to ``NEUTRAL`` rather
    than inventing corroboration. Token sets are ignored — NLI reads raw content.
    """

    name = "nli"

    def __init__(self, model_name: str, *, min_prob: float = 0.5) -> None:
        try:
            from sentence_transformers import CrossEncoder
        except ImportError as exc:
            raise RuntimeError(
                "SCP_TRUST_NLI is set but sentence-transformers is not installed. "
                "Install the NLI dependencies: pip install 'scp-memory-core[embeddings]'."
            ) from exc
        # Cross-encoders for NLI emit logits over (contradiction, entailment, neutral).
        self._model = CrossEncoder(model_name)
        self._min_prob = min_prob
        self._labels = (Relation.CONFLICT, Relation.AGREE, Relation.NEUTRAL)

    def relate(
        self,
        a: Memory,
        b: Memory,
        a_tokens: set[str],
        b_tokens: set[str],
        *,
        config: TrustConfig,
    ) -> Relation:
        import numpy as np

        logits = self._model.predict([(a.content, b.content)])[0]
        probs = _softmax(np.asarray(logits, dtype=float))
        idx = int(probs.argmax())
        if probs[idx] < self._min_prob:
            return Relation.NEUTRAL
        return self._labels[idx]


def _softmax(x):  # pragma: no cover - exercised only on the NLI path
    import numpy as np

    z = x - x.max()
    e = np.exp(z)
    return e / e.sum()


@lru_cache
def get_relation_detector() -> RelationDetector:
    """Resolve the configured relation detector (cached for the process)."""
    settings = get_settings()
    if settings.trust_nli:  # pragma: no cover - integration-only
        logger.info("trust relation detector: nli (%s)", settings.trust_nli_model)
        return NliRelationDetector(settings.trust_nli_model)
    return LexicalRelationDetector()
