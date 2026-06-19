# 19 — UI Design System

**Status:** Design intent · **Primary target:** Phase 7 (Admin Console) + Phase 8 (Android) · **Last updated:** 2026-06-20

The front-end design language for the Admin Console and reference apps. Use the
`/frontend-design` skill when building UI.

## Design Goals

Premium · Minimal · Professional · Fast · Accessible.

Inspiration: **Linear · Stripe · Vercel · Datadog · GitHub** — dense but calm,
information-rich, keyboard-first, restrained color.

## Foundations

- **Typography:** Inter.
- **Layout:** 8-point grid; generous whitespace; content-first.
- **Themes:** Light and Dark (first-class, not an afterthought).
- **Color:** neutral base, restrained accent; semantic colors for trust/state.
- **Motion:** subtle, purposeful; never blocking.

## Primary Screens (Phase 7)

- **Dashboard** — system health, memory counts, retrieval/trust at a glance.
- **Memory Explorer** — browse/search/inspect memories, states, provenance.
- **Retrieval Inspector** — run a query, see candidates and per-signal scores
  (explainability made visible).
- **Trust Explorer** — inspect provenance/confidence/freshness and explanations.
- **Benchmarks** — latency/quality trends ([21-benchmark-results](21-benchmark-results.md)).
- **Settings** — namespaces, policies, deployment config.

## Required States (every screen)

- **Empty** — clear, instructive first-run state.
- **Loading** — skeletons, no layout shift.
- **Error** — actionable, non-technical messaging.
- **Keyboard navigation** — full keyboard operability.
- **Accessibility** — WCAG AA: contrast, focus order, ARIA, reduced-motion.

## Principles

- Make explainability **visual** — the UI's job is to show *why* a memory was
  retrieved/ranked and *how trustworthy* it is.
- Fast by default; perceived performance matters.

## Related

[03-system-architecture](03-system-architecture.md) · [13-retrieval-model](13-retrieval-model.md) · [15-trust-model](15-trust-model.md) · [23-roadmap](23-roadmap.md)
