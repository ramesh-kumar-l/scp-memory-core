"""Benchmark seed (21-benchmark-results).

Self-contained stdlib timing — no extra plugin. Opt-in: ``pytest -m benchmark``.
Asserts a generous latency ceiling so it doubles as a regression guard; precise
numbers are recorded in 21-benchmark-results at milestones.
"""

import time

import pytest

from scp_memory.schemas.memory import MemoryCreate
from scp_memory.services import memory_service

pytestmark = pytest.mark.benchmark


def test_create_latency_seed(db):
    n = 200
    start = time.perf_counter()
    for i in range(n):
        memory_service.create(
            db, MemoryCreate(content=f"memory {i}", namespace="bench"), actor="bench"
        )
    elapsed = time.perf_counter() - start
    per_op_ms = (elapsed / n) * 1000
    # Generous ceiling for CI variance; tighten as the store evolves.
    assert per_op_ms < 50, f"create p_avg={per_op_ms:.2f}ms exceeded ceiling"
