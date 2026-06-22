# 02 — Pareto Ranking

Each candidate artifact (from [`01-artifact-inventory.md`](01-artifact-inventory.md))
scored 1–10 on five impact axes and an **Effort** axis (1 = trivial, 10 = huge).

**Leverage Score** = `(Career + OpenSource + Startup + Learning + Distribution) / Effort`
— value per unit of effort. Higher = ship first.

> Scores are judgment calls for a Principal/CAREER objective with startup optionality.
> The ranking is the deliverable; absolute numbers matter less than the ordering.

| Rank | Artifact | Career | OSS | Startup | Learn | Distrib | Effort | **Leverage** |
|---|---|---|---|---|---|---|---|---|
| 1 | C1 Principal case study | 10 | 4 | 6 | 7 | 6 | 3 | **11.0** |
| 2 | R1 Engineering thesis | 9 | 7 | 8 | 6 | 8 | 4 | **9.5** |
| 3 | D1 Blog series (6–8) | 9 | 9 | 7 | 8 | 10 | 5 | **8.6** |
| 4 | E1 Production README | 7 | 10 | 7 | 4 | 9 | 4 | **9.3** |
| 5 | A1 Architecture doc | 9 | 7 | 6 | 8 | 6 | 4 | **9.0** |
| 6 | E3 Golden examples + seed | 7 | 9 | 7 | 7 | 8 | 4 | **9.5** |
| 7 | A2 ADR collection | 9 | 6 | 5 | 9 | 5 | 4 | **8.5** |
| 8 | E2 Quick Start guide | 5 | 10 | 6 | 4 | 8 | 3 | **11.0** |
| 9 | E4 Benchmark report | 9 | 7 | 7 | 7 | 7 | 5 | **7.4** |
| 10 | C5 Talk / deck | 8 | 6 | 6 | 5 | 9 | 5 | **6.8** |
| 11 | P4 / O3 Public roadmap | 6 | 8 | 7 | 3 | 6 | 2 | **15.0**¹ |
| 12 | L1 Reusable asset catalog | 7 | 5 | 4 | 9 | 4 | 3 | **9.7**¹ |
| 13 | C2/C3 Resume + LinkedIn | 9 | 2 | 3 | 2 | 8 | 2 | **12.0**¹ |
| 14 | D2 Launch thread / Show HN | 6 | 9 | 6 | 3 | 10 | 3 | **11.3**¹ |
| 15 | C4 System-design narrative | 9 | 2 | 4 | 6 | 4 | 3 | **8.3** |
| 16 | A3/A4 Diagram pack | 6 | 7 | 5 | 5 | 8 | 4 | **7.8** |
| 17 | D3 Loom/GIF demo | 5 | 8 | 6 | 2 | 9 | 4 | **7.5** |
| 18 | O5 PyPI/npm publish | 4 | 9 | 6 | 4 | 7 | 4 | **7.5** |
| 19 | N1 Security white paper | 5 | 5 | 8 | 4 | 4 | 6 | **4.3** |
| 20 | E7 SDK reference docs | 4 | 8 | 5 | 3 | 5 | 5 | **5.0** |
| 21 | O6 Docs site | 5 | 8 | 6 | 3 | 7 | 7 | **4.1** |
| 22 | M1–M4 Community infra | 3 | 7 | 5 | 3 | 6 | 6 | **4.0** |
| 23 | N4 Pricing/open-core doc | 3 | 3 | 9 | 4 | 3 | 5 | **4.4** |

¹ High leverage but **supporting/derivative** — they ride on the top artifacts (e.g.
the launch thread is empty without the README + blog; resume bullets derive from the case
study). They're cheap *finishers*, scheduled in the execution plan rather than counted as
one of the 10 primary builds.

## Reading the ranking

Three clusters emerge:

1. **Narrative spine (do first):** Case study, Engineering thesis, Architecture doc, ADRs.
   These convert existing work into *credibility* and are the source material everything
   else reuses.
2. **Distribution surface (do next):** Production README, Quick Start, Golden examples,
   Blog series, Talk. These put the work in front of people and let them run it in one
   command.
3. **Proof + finishers:** Benchmark report, roadmap, reusable catalog, then the cheap
   derivatives (resume/LinkedIn/launch thread) that compound the above.

The selected 10 in [`03-the-80-20-artifact-set.md`](03-the-80-20-artifact-set.md) take
the spine + distribution surface + the benchmark proof, satisfying every mandatory
category (Architecture, Engineering, Career, Distribution, Open Source, Learning).
