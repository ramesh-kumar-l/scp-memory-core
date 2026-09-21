"""Trust-calibration harness (24-known-risks R3).

Run: ``python -m evals.run_trust_calibration``

Scores every item in ``datasets/trust_eval.json`` with the engine's trust layer,
treats the resulting **confidence** as a predicted probability of correctness, and
measures it against the dataset's ground-truth ``correct`` labels. Prints a
reliability table plus Brier score and Expected Calibration Error.

This is the gate for the lexical→NLI swap: only enable ``SCP_TRUST_NLI`` once it
measurably lowers ECE/Brier here. Switch detectors by exporting the flag before
running (the harness uses whatever ``get_relation_detector`` resolves).
"""

from evals.calibration import (
    brier_score,
    expected_calibration_error,
    reliability_table,
)
from evals.loader import build_memory, group_by_namespace, load_dataset
from scp_memory.services import trust_service
from scp_memory.services.relation_detector import get_relation_detector
from scp_memory.utils.time import utcnow


def score_dataset(items: list[dict]) -> tuple[list[float], list[int]]:
    """Return (predicted_confidence, observed_correct) aligned across all items."""
    now = utcnow()
    confidence_by_id: dict[str, float] = {}
    for group in group_by_namespace(items).values():
        memories = [build_memory(it, now=now) for it in group]
        for item, result in zip(group, trust_service.evaluate_all(memories, now=now), strict=True):
            confidence_by_id[item["id"]] = result.confidence
    probs = [confidence_by_id[it["id"]] for it in items]
    outcomes = [1 if it["correct"] else 0 for it in items]
    return probs, outcomes


def report(items: list[dict]) -> dict[str, float]:
    """Score, print a human report, and return the summary metrics."""
    probs, outcomes = score_dataset(items)
    brier = brier_score(probs, outcomes)
    ece = expected_calibration_error(probs, outcomes, bins=5)

    detector = get_relation_detector().name
    print(f"\nTrust calibration - detector: {detector}  (n={len(items)})")
    print("-" * 64)
    print(f"{'confidence bin':>16} {'count':>6} {'avg_conf':>9} {'avg_acc':>9}")
    for b in reliability_table(probs, outcomes, bins=5):
        print(
            f"  [{b.lo:.1f}, {b.hi:.1f}){'':>4} {b.count:>6} "
            f"{b.avg_confidence:>9.3f} {b.avg_accuracy:>9.3f}"
        )
    print("-" * 64)
    print(f"Brier score (lower better) : {brier:.4f}")
    print(f"Expected calib. error (ECE): {ece:.4f}")
    print(
        "\nInterpretation: rows where avg_conf >> avg_acc are over-confident "
        "(e.g. lexical false corroboration of semantic contradictions). A lower "
        "ECE under SCP_TRUST_NLI is the signal to adopt it.\n"
    )
    return {"brier": brier, "ece": ece}


def main() -> None:
    data = load_dataset("trust_eval.json")
    report(data["items"])


if __name__ == "__main__":
    main()
