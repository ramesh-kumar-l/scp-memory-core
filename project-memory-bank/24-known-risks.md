# 24 — Known Risks

**Status:** Active register · **Last updated:** 2026-06-20

Likelihood × Impact, with mitigations. Revisit each phase boundary.

| # | Risk | L | I | Mitigation |
|---|---|---|---|---|
| R1 | **Scope creep** — building ahead of the active phase | M | H | Strict one-phase model; stop + approval at boundaries ([08](08-active-phase.md)); backlog gates work |
| R2 | **Retrieval quality** — hybrid retrieval returns irrelevant memories | M | H | Benchmark-driven fusion choice; precision/recall tracking ([21](21-benchmark-results.md)) |
| R3 | **Trust mis-calibration** — confidence misleads consumers | M | H | **In progress (2026-06-20):** trust-calibration harness now exists (`evals/run_trust_calibration.py`, Brier/ECE over a fixed labelled set) and the **NLI seam is shipped opt-in** (`SCP_TRUST_NLI`, behind `RelationDetector`). Lexical baseline on the fixed set: Brier ≈ 0.17 / ECE ≈ 0.19, with measurable over-confidence on semantic contradictions. **Next:** run NLI through the harness; adopt only if it lowers ECE. Hermetic CI preserved (lexical default). Explainability lets users judge; trust is a signal not truth ([15](15-trust-model.md)) |
| R4 | **Performance** — latency at scale (vector + ranking) | M | M | Qdrant for ANN; bounded k; p95/p99 SLOs ([17](17-observability-model.md)) |
| R5 | **On-device constraints** — memory/CPU limits on Android | M | M | **In progress (2026-06-20):** Phase-8 app ships **hybrid** — thin client over the engine when reachable, else a local **Room** store + lightweight on-device retrieval/trust stand-in (mirrors the §9 contract, no engine math duplicated on the live path). Same domain model ([03](03-system-architecture.md)). **Next:** device build/run verification |
| R6 | **Data correctness** — vector/relational drift | L | H | Relational store is source of truth; write-through + reconciliation ([11](11-data-models.md)) |
| R7 | **Privacy/governance gaps** — leakage or improper retention | L | H | Namespacing, audit, governed delete, policies ([16](16-security-model.md)) |
| R8 | **Over-engineering** — speculative abstractions slow delivery | M | M | Simplicity-first principle; surgical changes ([05](05-engineering-principles.md)) |
| R9 | **Dependency risk** — Qdrant/Neo4j operational burden | L | M | Keep stores pluggable; evaluate pgvector as simpler alternative |
| R10 | **Explainability cost** — carrying signals adds complexity/overhead | L | M | Treat as core requirement; measure overhead in benchmarks |

## Notes

- R1 and R8 are the most acute *process* risks for this project's operating model.
- Promote any risk that materializes into an active initiative ([27](27-active-initiatives.md)).

## Related

[05-engineering-principles](05-engineering-principles.md) · [15-trust-model](15-trust-model.md) · [16-security-model](16-security-model.md)
