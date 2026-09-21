"""Trust layer — pure, I/O-free scoring (Phase 4, 15-trust-model).

Trust is a first-class, retrievable dimension: provenance quality, confidence
(corroboration/contradiction), and freshness, plus a human-readable explanation.
These modules combine numbers only; the DB-aware orchestration that gathers those
numbers lives in ``scp_memory.services.trust_service``.
"""
