"""Shared eval helpers: path bootstrap, dataset loading, transient memories.

The harnesses run the engine's pure scorers without a database — they build
transient ``Memory`` objects straight from a labelled dataset. Kept here so both
the trust and retrieval harnesses share one definition.
"""

import json
import sys
from datetime import timedelta
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:  # let the harnesses run without an editable install
    sys.path.insert(0, str(_SRC))

from scp_memory.models.memory import Memory  # noqa: E402
from scp_memory.models.provenance import Provenance  # noqa: E402
from scp_memory.utils.time import utcnow  # noqa: E402

DATASETS = Path(__file__).resolve().parent / "datasets"


def load_dataset(name: str) -> dict:
    """Load a JSON dataset from ``evals/datasets`` by file name."""
    return json.loads((DATASETS / name).read_text(encoding="utf-8"))


def build_memory(item: dict, *, now=None) -> Memory:
    """Build a transient (session-less) ``Memory`` from a dataset item."""
    now = now or utcnow()
    memory = Memory(
        id=item["id"],
        content=item["content"],
        type=item["type"],
        namespace=item["namespace"],
        created_at=now - timedelta(days=float(item.get("age_days", 0))),
        importance=float(item.get("importance", 0.5)),
    )
    memory.provenance = Provenance(memory_id=item["id"], source=item.get("source", "user"))
    return memory


def group_by_namespace(items: list[dict]) -> dict[str, list[dict]]:
    """Group dataset items by namespace (corroboration is namespace-scoped)."""
    groups: dict[str, list[dict]] = {}
    for item in items:
        groups.setdefault(item["namespace"], []).append(item)
    return groups
