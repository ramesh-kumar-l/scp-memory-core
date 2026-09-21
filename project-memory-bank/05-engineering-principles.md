# 05 — Engineering Principles

**Status:** Active · **Phase:** 0 · **Last updated:** 2026-06-20

## Principles

1. **Build incrementally.** Never rewrite working code. Extend existing
   implementation. Surgical changes only.
2. **Understand before implementing.** Read the memory bank first. Justify every
   decision. Surface assumptions and tradeoffs; ask when unclear.
3. **Simplicity beats cleverness.** Minimum code that solves the problem. No
   speculative abstractions, configurability, or error handling for impossible
   cases.
4. **Reliability beats features.** A smaller, correct, well-tested surface beats
   a large fragile one.
5. **One phase at a time.** Never work ahead. Stop at phase boundaries and await
   explicit approval.
6. **Documentation is mandatory.** Code without docs/tests/metrics is incomplete.
7. **Explainability is a feature.** Retrieval and ranking must expose their
   signals. No black boxes.
8. **Trust is first-class.** Provenance, confidence, and freshness are part of
   the model, not an afterthought.
9. **Portable by design.** Same domain model on-device and in cloud. Storage is
   pluggable; the domain model is stable.

## Quality Gates

No feature is complete until **all** of these are satisfied:

- ✅ Architecture reviewed
- ✅ API defined ([10-api-contracts](10-api-contracts.md))
- ✅ Tests added ([18-testing-strategy](18-testing-strategy.md))
- ✅ Logging added
- ✅ Metrics added ([17-observability-model](17-observability-model.md))
- ✅ Documentation added
- ✅ Benchmark added ([21-benchmark-results](21-benchmark-results.md))
- ✅ Examples added

## Working Agreement

- Memory bank is the source of truth — consult before every task; update after
  every approved phase (`07`, `08`, `28`).
- Token efficiency: load the smallest set of files needed; never scan the repo.
- Every changed line should trace directly to the current task/phase.

## Related

[00-project-charter](00-project-charter.md) · [18-testing-strategy](18-testing-strategy.md) · [06-technical-decisions](06-technical-decisions.md)
