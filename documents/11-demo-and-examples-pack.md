# 11 — Demo & Examples Pack (10 Golden Examples)

> **Artifact 8 of the 80/20 set.** Turns "read about it" into "run it and *see* the trust
> scores." Ten curated memories, each chosen to showcase one differentiator. Seeded into
> **both** the engine DB and the Android device DB from one shared dataset:
> [`golden-examples.json`](golden-examples.json).

---

## The 10 golden examples

Namespace: **`demo:golden`**. Each example demonstrates a specific capability.

| ID | Type | Content (abbrev.) | Provenance | Demonstrates |
|---|---|---|---|---|
| `mem_gold_darkmode` | preference | "User prefers dark mode" | user (1.0) | Baseline high-provenance preference |
| `mem_gold_lightmode` | preference | "Switched to light mode; no longer wants dark mode" | user (1.0) | **Contradiction** vs darkmode + recency/freshness |
| `mem_gold_staffgoal` | preference | "Wants to become a staff engineer within 2 years" | user (1.0) | Source memory for consolidation |
| `mem_gold_meetings` | preference | "Dislikes long meetings" | inferred (0.5) | **Inferred** provenance → lower confidence floor |
| `mem_gold_summary` | summary | "Pursuing staff-engineer role; prefers short, focused meetings" | consolidation (0.75) | **Consolidation** with `derived_from` |
| `mem_gold_dinner` | event | "Spent ₹2450 on dinner at a Goa beach shack, paid by card" | user (1.0) | **Metadata-rich** finance retrieval (amount/category) |
| `mem_gold_netflix` | fact | "Netflix renews on the 18th at ₹649/month" | user (1.0) | Recurring fact; slow freshness decay |
| `mem_gold_goatrip` | event | "Goa beach trip — sunset photos with college friends" | user (1.0) | **Gallery** (media) + **event decay** (35 days old) |
| `mem_gold_flight` | event | "Flight DEL→GOI, seat 14A, ₹8200 — biggest trip expense" | user (1.0) | **Hybrid retrieval** by route/semantics |
| `mem_gold_timezone` | fact | "Timezone set to IST (Asia/Kolkata) at onboarding" | system (0.4) | **System** provenance → lowest trust floor |

### Why these ten
Together they exercise the **entire trust + lifecycle surface**: the full provenance
spectrum (user → consolidation → inferred → system), a **contradiction** pair (the headline
demo), a **consolidation summary** with real `derived_from`, **type-aware freshness** (a
35-day `event` decays far more than a 60-day `preference`), and **metadata/hybrid
retrieval** across the three golden use cases (Assistant Memory, Personal Finance, Semantic
Gallery).

## Demo queries (what to run after seeding)

| Query | Expect | Proves |
|---|---|---|
| `"what theme does the user like?"` | both theme memories surface, each trust-scored; light-mode ranks above dark-mode **on-device / with real embeddings** | Contradiction + freshness in ranking |
| `"how much did I spend in Goa?"` | dinner (₹2450) + flight (₹8200) | Metadata + hybrid retrieval |
| `"show me my beach trip"` | Goa trip photo memory, by *event* not filename | Semantic gallery |
| `"what are the user's career goals?"` | staff-engineer goal + the consolidation summary | Consolidation + provenance |
| `GET /v1/trust/<timezone id>` | low provenance_quality (0.4), explained | System-source trust floor |

> **Reliable on every path:** each result carries `signals` + `weights` + a `trust`
> breakdown, and trust **scores** track provenance (system 0.4 < inferred 0.5 <
> consolidation 0.75 < user 1.0). **Best on-device / with real embeddings:** the
> *ranking* effect of freshness + contradiction (the hermetic engine mutes freshness and
> uses a stand-in embedder, so exact order there is approximate).

## Seed & verify — Engine (`scp-memory-core`)

```bash
# 1) start the engine (serves the DB the console reads)
python -m scp_memory            # http://localhost:8000

# 2) seed the 10 golden examples over the HTTP API
python seed/seed_golden_examples.py            # --base-url http://localhost:8000
#    quick, no-server check:
python seed/seed_golden_examples.py --in-process

# 3) verify
#    - the script prints the created count + a sample trust-scored search
#    - or open the Admin Console → Memory Explorer (namespace = demo:golden)
#    - or: curl 'localhost:8000/v1/memories?namespace=demo:golden'

# reset
python seed/seed_golden_examples.py --reset
```

> **Engine vs device freshness:** the engine is a live system — `recorded_at` is set to
> *now* on create, so the freshness/decay demo is muted there (everything is fresh). The
> Android seeder writes the Room DB **directly** and *backdates* `created_at`, so decay is
> visible on-device. This difference is intentional and honest, not a bug.

## Seed & verify — Android (`SCPMemoryEngine_AndroidReferenceApp`)

```bash
# app must be launched once so Room has created the schema
python seed/seed_golden_device.py              # writes Room DB via adb run-as; backdates ages
#   reads ../../scp-memory-core/documents/golden-examples.json by default (--dataset to override)
# verify: launch the app → Explore screen → namespace demo:golden
python seed/seed_golden_device.py --reset      # clear only the demo:golden namespace
```

## Verification checklist

- [ ] Engine: `GET /v1/memories?namespace=demo:golden` returns **10** items.
- [ ] Engine: search `"what theme does the user like?"` returns results that each carry
  `signals` + `trust.explanation`; the consolidation summary shows `trust.confidence`
  **0.75** and the system-sourced memory the lowest provenance.
- [ ] Engine: the summary memory's `/v1/trust/{id}` shows provenance_quality **0.75**
  (and `derived_from` is set on the **Android** path, which writes it directly).
- [ ] Android: Explore screen shows the 10 memories; the Goa trip renders its image; the
  35-day event shows lower freshness than the 60-day preference.

## Files

- Dataset: [`golden-examples.json`](golden-examples.json) (single source of truth)
- Engine seeder: [`../seed/seed_golden_examples.py`](../seed/seed_golden_examples.py)
- Android seeder: `../../SCPMemoryEngine_AndroidReferenceApp/seed/seed_golden_device.py`
- Seed tooling notes: [`../seed/README.md`](../seed/README.md)
