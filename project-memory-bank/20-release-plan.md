# 20 — Release Plan

**Status:** Active · **Phase:** 0 · **Last updated:** 2026-06-20

## Versioning

- **Semantic Versioning** (`MAJOR.MINOR.PATCH`).
- Pre-1.0 (`0.x`) during Phases 1–4: API may change between minors; changes are
  documented in the changelog and ADRs.
- **1.0.0** targeted when the Trust Layer (Phase 4) is stable and the Python SDK
  (Phase 5) is published — i.e., the core promise (persistent + retrievable +
  trustworthy + explainable) is fully shippable.

## Milestone → Release Mapping

| Phase | Release | Notes |
|---|---|---|
| 0 | `0.0.0` (foundation) | Memory bank only; no package |
| 1 | `0.1.0` | Memory Core: CRUD + audit |
| 2 | `0.2.0` | Memory Intelligence |
| 3 | `0.3.0` | Hybrid Retrieval + ranking |
| 4 | `0.4.0` → `1.0.0` candidate | Trust Layer; 1.0 when stable |
| 5 | `1.x` | SDKs (Python, then TypeScript) |
| 6 | `1.x` | Observability |
| 7 | `1.x` | Admin Console |
| 8 | `1.x` | Android reference app |

## Release Checklist (per release)

- [ ] Quality gates passed (see [05-engineering-principles](05-engineering-principles.md))
- [ ] Changelog updated
- [ ] ADRs recorded for notable decisions ([25-adr-log](25-adr-log.md))
- [ ] Benchmark report updated ([21-benchmark-results](21-benchmark-results.md))
- [ ] GitHub release notes
- [ ] Docs + examples updated
- [ ] Public artifacts produced ([26-public-artifacts](26-public-artifacts.md))

## Public Build Cadence

Per the public-build strategy, each milestone ships: ADR, architecture diagram,
technical blog, changelog, benchmark report, and GitHub release notes.

## Related

[23-roadmap](23-roadmap.md) · [26-public-artifacts](26-public-artifacts.md) · [25-adr-log](25-adr-log.md)
