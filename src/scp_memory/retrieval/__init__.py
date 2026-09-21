"""Hybrid retrieval (Phase 3): keyword + vector + metadata + ranking fusion.

This package holds the **pure, I/O-free** retrieval logic — embeddings, lexical
scoring, and score fusion. DB-aware orchestration lives in
``services.retrieval_service``; pluggable nearest-neighbour search lives in
``services.vector_backend``. See 13-retrieval-model and 14-ranking-model.
"""
