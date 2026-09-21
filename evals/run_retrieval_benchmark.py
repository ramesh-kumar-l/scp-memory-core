"""Weighted-vs-RRF fusion benchmark (14-ranking-model).

Run: ``python -m evals.run_retrieval_benchmark``

Loads ``datasets/retrieval_eval.json`` into an in-memory engine, runs every query
under both fusion strategies (weighted-linear, the explainable default, and
reciprocal-rank fusion), and reports nDCG@k and MRR for each. This is the evidence
behind the ranking-model default; re-run it when signals or weights change.
"""

import scp_memory.models  # noqa: F401  (register tables)
from evals import loader  # noqa: F401  (bootstraps sys.path for scp_memory)
from evals.loader import load_dataset
from evals.retrieval_quality import mrr, ndcg_at_k, precision_at_k
from scp_memory.db.base import Base
from scp_memory.models.enums import MemoryType
from scp_memory.schemas.memory import MemoryCreate
from scp_memory.schemas.retrieval import RetrieveRequest
from scp_memory.services import memory_service, retrieval_service

_METHODS = ("weighted", "rrf")


def _build_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool, future=True
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)()


def _load_corpus(db, data: dict) -> dict[str, str]:
    """Insert the corpus; return {local_id: engine_id}."""
    id_map: dict[str, str] = {}
    for doc in data["corpus"]:
        created = memory_service.create(
            db,
            MemoryCreate(
                content=doc["content"],
                namespace=data["namespace"],
                type=MemoryType(doc["type"]),
                source=doc.get("source"),
            ),
            actor="benchmark",
        )
        id_map[doc["id"]] = created.id
    return id_map


def evaluate(data: dict, method: str, id_map: dict[str, str], db) -> dict[str, float]:
    """Run all queries under one fusion method; return aggregate metrics."""
    k = int(data.get("k", 5))
    rankings: list[tuple[list[str], set[str]]] = []
    ndcgs: list[float] = []
    precisions: list[float] = []
    for q in data["queries"]:
        req = RetrieveRequest(query=q["query"], namespace=data["namespace"], k=k, mode="hybrid")
        results = retrieval_service.search(db, req, touch=False, fuse_method=method)
        ranked_ids = [r.memory.id for r in results]
        relevant = {id_map[r] for r in q["relevant"]}
        rankings.append((ranked_ids, relevant))
        ndcgs.append(ndcg_at_k(ranked_ids, relevant, k))
        precisions.append(precision_at_k(ranked_ids, relevant, k))
    return {
        "ndcg": sum(ndcgs) / len(ndcgs),
        "mrr": mrr(rankings),
        "precision": sum(precisions) / len(precisions),
        "k": k,
    }


def report(data: dict) -> dict[str, dict[str, float]]:
    db = _build_db()
    id_map = _load_corpus(db, data)
    results = {m: evaluate(data, m, id_map, db) for m in _METHODS}
    k = results[_METHODS[0]]["k"]

    print(f"\nRetrieval fusion benchmark  (queries={len(data['queries'])}, k={int(k)})")
    print("-" * 52)
    print(f"{'method':>10} {'nDCG@k':>9} {'MRR':>9} {'P@k':>9}")
    for method in _METHODS:
        r = results[method]
        print(f"{method:>10} {r['ndcg']:>9.3f} {r['mrr']:>9.3f} {r['precision']:>9.3f}")
    print("-" * 52)
    best = max(_METHODS, key=lambda m: results[m]["ndcg"])
    print(f"Higher nDCG wins. Best on this set: {best}.\n")
    db.close()
    return results


def main() -> None:
    report(load_dataset("retrieval_eval.json"))


if __name__ == "__main__":
    main()
