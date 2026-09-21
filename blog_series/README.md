# Blog Series — Trust-Aware Memory for AI Agents

Seven publish-ready, deep-dive articles that turn `scp-memory-core` into a body of writing.
Each is 1,500–2,500 words, diagram-first (mermaid), with runnable code and an honest
tradeoffs section. Editorial plan + distribution checklist:
[`../documents/10-blog-series-plan.md`](../documents/10-blog-series-plan.md).

| # | Title | Read |
|---|---|---|
| 1 | Why AI Agents Need a Memory Layer, Not a Bigger Vector Index | [`01-why-agents-need-a-memory-layer.md`](01-why-agents-need-a-memory-layer.md) |
| 2 | Designing Trust as a First-Class Signal in Agent Memory | [`02-trust-as-a-first-class-signal.md`](02-trust-as-a-first-class-signal.md) |
| 3 | Explainable Hybrid Retrieval You Can Actually Debug | [`03-explainable-hybrid-retrieval.md`](03-explainable-hybrid-retrieval.md) |
| 4 | Memory Has a Lifecycle: Importance, Dedup, Consolidation, Decay | [`04-memory-lifecycle.md`](04-memory-lifecycle.md) |
| 5 | Calibrate Before You Sophisticate: Gating Model Swaps with Brier & ECE | [`05-calibrate-before-you-sophisticate.md`](05-calibrate-before-you-sophisticate.md) |
| 6 | Hermetic by Default, Pluggable at Scale: Backend Seams Done Right | [`06-hermetic-by-default-pluggable-at-scale.md`](06-hermetic-by-default-pluggable-at-scale.md) |
| 7 | Governing Agent Memory: Namespacing, Audit, and the Right to Be Forgotten | [`07-governing-agent-memory.md`](07-governing-agent-memory.md) |

## Publishing notes

- **Order matters:** post 1 is the category argument and anchors the launch; 2–7 go deeper.
- **Canonical** on your blog/Medium; mirror to dev.to with `canonical_url`. Mermaid renders
  natively on GitHub and most platforms; export a PNG of the lead diagram for the social
  preview image.
- Each post links the repo in the first and last section and points to the next post.
- Tags: `ai`, `llm`, `agents`, `machine-learning`, `software-architecture`.

> Rendering note: GitHub renders ```mermaid blocks automatically. On Medium, paste the PNG
> exports; keep the mermaid source in the canonical copy so the diagrams stay editable.
