"""Offline evaluation harnesses for the SCP Memory Engine.

These are *measurement* tools, not part of the served engine: they run the pure
scorers over fixed, labelled datasets so a human can decide whether a change
(e.g. NLI trust, RRF fusion) actually improves quality before shipping it.

- ``calibration`` + ``run_trust_calibration`` — is predicted trust confidence
  calibrated against observed correctness? (gates the NLI swap, 24-known-risks R3)
- ``retrieval_quality`` + ``run_retrieval_benchmark`` — weighted fusion vs RRF on
  a labelled retrieval set (nDCG / MRR), the 14-ranking-model decision.
"""

import sys
from pathlib import Path

# Make ``scp_memory`` importable when the harnesses run without an editable
# install (e.g. ``python -m evals.run_retrieval_benchmark`` from a clean checkout).
# Lives in the package __init__ so it runs before any submodule body, independent
# of import ordering.
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
