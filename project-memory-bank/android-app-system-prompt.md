# SCP Memory Engine — Android Reference App: System Prompt / Specification

> **This file is the ONLY input given to Claude Design.** It is self-contained:
> everything required to design and implement the Android Reference Application is
> here. Do **not** request architecture files, ADRs, source code, or backend
> internals — they are not needed and not available.
>
> **You are designing and implementing an Android app.** Do not redesign the
> backend. Do not invent new APIs, domain models, trust models, or memory models —
> reuse the contracts in §9 verbatim.

---

## 1. Product Overview

**SCP Memory Engine** is a memory-infrastructure layer for AI systems: it stores
durable "memories," retrieves them with a hybrid (keyword + semantic + metadata)
search, and attaches a **trust** signal and an **explanation** to every result.
Its defining promise is **explainability** — you can always answer *"why was this
remembered, why was it retrieved, and how much should I trust it?"*

The **Android Reference App** is **not the product**. It is the:

> "Reference implementation of SCP Memory Engine demonstrating on-device semantic
> memory."

Its job is to **showcase the engine** through a clean, professional mobile UI that
makes five capabilities tangible:

1. **Memory Storage** — capture a memory with type + provenance.
2. **Semantic Retrieval** — ask in natural language, get relevant memories.
3. **Memory Exploration** — browse, filter, and inspect the memory store.
4. **Trust Inspection** — see provenance, confidence, freshness, and the
   explanation behind any memory.
5. **Explainability** — visualize *why* a result ranked where it did (per-signal
   score breakdown).

It is a thin, faithful client over the engine's HTTP API (§9). All intelligence
lives in the engine; the app renders and explains it.

---

## 2. Product Goals

- **Demonstrate, don't reimplement.** Every screen exists to surface an engine
  capability. No business logic (scoring, ranking, trust math) in the app.
- **Make explainability visual.** The hero interaction is seeing the *signals and
  trust* behind a result, not just a list of hits.
- **Feel like a mobile Admin Console.** Visual continuity with the Phase-7 web
  console: Inter, 8-pt grid, light+dark, restrained color, semantic trust/state
  colors.
- **Production-credible.** Required Empty / Loading / Error states on every screen,
  full accessibility (WCAG AA), keyboard/switch/TalkBack operability, no jank.
- **Demoable in 5 minutes.** Ship seed scenarios (§17) so the value is obvious
  immediately without manual setup.

**Success = a reviewer can, in one sitting:** store a memory, ask a natural-language
question, get a ranked answer, tap into its trust breakdown, and understand exactly
why it was retrieved.

---

## 3. Target Users

| User | Need | What they look at |
|---|---|---|
| **Engineering evaluator** (lead/architect deciding whether to adopt SCP) | Proof the engine is explainable and trustworthy, not a black-box vector DB | Trust Explorer, Retrieval signal breakdown |
| **Developer integrator** | A concrete reference for how a client consumes the API | Whole app as a worked example; Settings (endpoint config) |
| **Product / design stakeholder** | A tangible story of "AI memory you can trust" | Dashboard, Search, demo scenarios |
| **Internal demo presenter** | A reliable, fast, good-looking walkthrough | Seeded scenarios, smooth states |

Not targeted: end-consumers managing personal notes. This is a **showcase/reference**
tool for a technical audience.

---

## 4. Core Use Cases

1. **Store a memory** with a type (fact/event/preference) and provenance, see it
   land in the store with an audit entry.
2. **Search semantically** — type a natural-language query, get ranked memories
   with per-signal scores.
3. **Explore the store** — browse/filter by type and state; understand lifecycle
   (active / consolidated / decayed / archived).
4. **Inspect a memory** — full content, metadata, provenance, lifecycle state, and
   audit trail.
5. **Inspect trust** — provenance quality, confidence, freshness, and the
   human-readable explanation, with their inputs.
6. **Understand retrieval** — for a given result, see why it ranked where it did
   (keyword/vector/metadata/importance/trust contributions + weights).
7. **Govern a memory** — soft-delete (and see it leave default retrieval while its
   audit persists).
8. **Review audit** — the append-only history of changes to a memory.

---

## 5. User Journeys

### J1 — "Can I trust this?" (the headline journey)
Dashboard → Search ("what theme does the user prefer?") → result list with score
bars → tap top result → Memory Detail → tap **Trust** → Trust Explorer shows
confidence 0.75 (corroborated by 2), freshness 0.6 (12 days old), provenance 0.9
(user-stated) + plain-English explanation. Evaluator concludes: *explainable, not
magic.*

### J2 — "Capture and recall"
Dashboard → **+ Store Memory** → enter "User upgraded to Pro plan on 2026-06-01",
type=event, provenance=user → save → confirmation + audit entry → Search ("when did
they upgrade?") → the event surfaces with high vector + freshness signals.

### J3 — "Explore the lifecycle"
Memory Explorer → filter `state=decayed` → see down-weighted memories retained for
audit → open one → Detail shows importance dropped + decay audit event → understand
memories aren't deleted, they're de-prioritized.

### J4 — "Why this and not that?"
Search → expand any result's **Explain** panel → compare two results' signal bars
side-by-meaning → see that result A won on vector similarity while result B had
higher trust → explainability made concrete.

### J5 — "Set it up against my engine"
First run → Settings → enter engine base URL + namespace + actor → connection check
→ Dashboard populates from `/health` + `/metrics`.

### Core User Flows (step-by-step)

The seven flows below are the testable spine of the app. Each lists trigger → steps
→ success → error/edge handling. They map 1:1 to acceptance criteria (§18).

**F1 — Store Memory.**
1. Trigger: FAB **+ Store Memory** (Dashboard/Explore) → opens `ModalBottomSheet`.
2. Enter `content` (required), pick `type` (fact/event/preference), pick provenance
   `source` (default `user`), optional metadata key/values.
3. Submit → `POST /v1/memories` with the active `namespace`/`actor` from Settings.
4. Success: sheet dismisses, snackbar "Memory stored", new memory appears at the top
   of Explore/Recent; an audit `created` event now exists.
5. Edge/error: empty content → inline field error (no request); 422 → field-level
   message; offline → submit disabled with "Connect to store" hint.

**F2 — Search Memory.**
1. Trigger: Search tab. Enter a natural-language query; choose `mode` (default
   hybrid); optionally set `k`, `min_confidence`, type filter.
2. Submit → `POST /v1/retrieval/search`.
3. Success: ranked result cards, each with fused `score`, trust chip, and a
   collapsible Explain panel (signal score bars + weights).
4. Edge: query ran, zero matches → **No-results** state (distinct from Empty) with
   "broaden query / lower min-confidence / switch mode" suggestions.
5. Error: request failed → inline error + Retry (query preserved).

**F3 — Inspect Memory.**
1. Trigger: tap a memory row/result anywhere → push **Memory Detail** (`memoryId`).
2. Load `GET /v1/memories/{id}` → render content, metadata, provenance, state,
   importance, timestamps.
3. Success: full detail with actions (Edit · Delete · Inspect Trust · View Audit).
4. Edge/error: 404 (deleted/missing) → "This memory no longer exists" → back to
   Explore; loading → skeleton.

**F4 — Inspect Trust.**
1. Trigger: **Inspect Trust** on Memory Detail, the trust chip on a result, or the
   Trust tab (pick a memory first) → push **Trust Explorer**.
2. Load `GET /v1/trust/{memory_id}`.
3. Success: confidence gauge + band, freshness (age + half-life), provenance
   (source + corroboration/contradiction counts), prominent explanation; if arrived
   from a result, the Ranking Factors panel renders the result's `signals`/`weights`.
4. Edge/error: trust unavailable → friendly error + Retry; tab opened with no memory
   selected → Empty prompt.

**F5 — View Retrieval Explanation.**
1. Trigger: expand a result's **Explain** panel (Search) or open Ranking Factors
   (Trust Explorer from a result).
2. Data: reuse the originating `POST /v1/retrieval/search` result — **no new call**.
3. Success: per-signal score bars (keyword/vector/metadata/importance/trust) with
   numeric values, the weights in effect, and the fused `score`, phrased as
   "scored 0.82 because vector 0.78 (w .3), trust 0.71 (w .2), …".
4. Edge: a signal absent for the chosen mode → show 0/"n/a", never fabricate.

**F6 — Delete Memory (governed).**
1. Trigger: Delete on Memory Detail, or swipe-to-delete in Explore.
2. Confirm dialog stating consequences (soft-delete by default; hard-delete behind
   an explicit toggle for compliance).
3. Submit → `DELETE /v1/memories/{id}` (`?hard=true` only if chosen).
4. Success: 204 → memory leaves default retrieval/Explore; snackbar with **Undo**
   affordance is optional but its audit trail persists and stays viewable.
5. Edge/error: offline → action disabled; 404 → treat as already gone; confirm
   required before any request fires.

**F7 — View Audit Trail.**
1. Trigger: **View Audit** on Memory Detail → push Audit Trail (`memoryId`).
2. Load `GET /v1/memories/{id}/audit`.
3. Success: reverse-chronological append-only list of events (action, actor, time,
   diff); visible even for soft-deleted memories.
4. Edge/error: empty (no events yet) → Empty state; error → Retry.

---

## 6. Navigation Model

**Bottom navigation bar** (Material 3 `NavigationBar`) with 4 primary destinations,
plus stacked detail routes via **Navigation Compose**.

```
Bottom Nav:
  ⌂ Dashboard      🔍 Search      ▤ Explore      ⛉ Trust
                                                   (+ Settings via top-app-bar action)

Stacked routes (pushed):
  Memory Detail        ← from Explore, Search, Dashboard
  Trust Explorer       ← from Memory Detail, Trust tab, a Search result
  Audit Trail          ← from Memory Detail
  Store Memory (modal/sheet) ← FAB on Dashboard & Explore
  Settings             ← top-app-bar gear (from any primary screen)
```

- **Single source of truth for navigation:** a `NavHost` with typed routes; deep
  arguments are `memoryId` and (optional) `query`.
- **FAB** (`+ Store Memory`) present on Dashboard and Explore.
- **Back** always returns to the originating primary tab; detail stacks preserve
  scroll state.
- **Trust Explorer** is reachable both as a top-level tab (pick a memory first) and
  contextually from a specific memory/result — it is a **first-class destination**,
  not a sub-panel.

---

## 7. Screen Specifications

Each screen lists **Purpose · Primary Actions · UI Components · States · Navigation
· Data Dependencies · Accessibility**. All screens must implement the five required
states from §11/§13 unless noted.

### 7.1 Dashboard
- **Purpose:** At-a-glance system health and store overview; the demo's landing pad.
- **Primary Actions:** Store Memory (FAB); jump to Search; open Settings.
- **UI Components:**
  - Health card — liveness/readiness from `/health`, `/health/ready` (status chip:
    ok/degraded/down).
  - Counters row — total memories, by-type and by-state counts (from list metadata
    / `/metrics` counters).
  - Retrieval & trust SLIs — request latency p50/p95 and op counters parsed from
    `/metrics` (client-side parse; no Grafana).
  - "Recent memories" list (last N created) → tap to Detail.
  - Connection banner if endpoint unreachable.
- **States:** Empty (no memories yet → CTA to store one / load demo seed), Loading
  (skeleton cards), Error (engine unreachable → retry + open Settings).
- **Navigation:** → Store Memory, → Search, → Memory Detail, → Settings.
- **Data Dependencies:** `GET /health`, `GET /health/ready`, `GET /metrics`,
  `GET /v1/memories?…&limit=N` (for counts/recent).
- **Accessibility:** status chips have text labels (not color-only); counters are
  grouped with content descriptions; latency numbers have units announced.

### 7.2 Memory Search
- **Purpose:** Natural-language semantic retrieval — the core capability.
- **Primary Actions:** Enter query; choose mode (hybrid/keyword/vector); set
  `min_confidence`; run; expand a result's explanation; open a result.
- **UI Components:**
  - Search field (multiline, with submit) + mode selector (segmented:
    Hybrid·Keyword·Vector) + advanced row (k slider, min-confidence slider, type
    filter chips).
  - Result list: each card shows content snippet, type badge, **fused score**, a
    compact **trust chip** (confidence), and an expandable **Explain** panel with
    per-signal **score bars** (keyword/vector/metadata/importance/trust) + weights.
  - Trust chip color reflects confidence band (semantic colors, §14).
- **States:** Empty (pre-search prompt + example queries from seed), Loading
  (result skeletons), Error (search failed → retry), **No-results** (distinct from
  empty: query ran, nothing matched → suggest broadening / lowering min-confidence).
- **Navigation:** result → Memory Detail; result trust chip → Trust Explorer.
- **Data Dependencies:** `POST /v1/retrieval/search`.
- **Accessibility:** score bars expose numeric value + label to TalkBack; the
  Explain panel is a proper expand/collapse with state announced; results are a
  semantic list with position info.

### 7.3 Memory Explorer
- **Purpose:** Browse/filter/inspect the whole store; understand lifecycle states.
- **Primary Actions:** Filter by type/state; paginate; open a memory; Store Memory
  (FAB); soft-delete (swipe or detail action).
- **UI Components:**
  - Filter bar: type chips (fact/event/preference/summary), state chips
    (active/consolidated/decayed/archived/deleted), namespace (from Settings).
  - Paged list of memory rows: content snippet, type badge, **state badge**,
    importance micro-bar, created/updated relative time.
  - Pull-to-refresh; infinite scroll (or pager) for `limit/offset`.
- **States:** Empty (no memories for filter → clear filters / store one), Loading
  (row skeletons), Error (retry).
- **Navigation:** row → Memory Detail; FAB → Store Memory.
- **Data Dependencies:** `GET /v1/memories?namespace=…&type=…&state=…&limit=&offset=`.
- **Accessibility:** state/type badges carry text; swipe-to-delete has an
  accessible equivalent action; filter chips announce selected state.

### 7.4 Memory Detail
- **Purpose:** Everything about one memory.
- **Primary Actions:** Edit content/metadata (PATCH); soft-delete (and hard-delete
  behind a confirm); open Trust Explorer; open Audit Trail.
- **UI Components:**
  - Header: type badge, state badge, importance bar, created/updated/last-accessed.
  - Content block (full text); metadata key/value list; provenance card
    (source: user/inferred/consolidation/system; derived_from links for summaries).
  - Trust summary strip (confidence/freshness/provenance mini-bars) → tap to Trust
    Explorer.
  - Actions: Edit · Delete · View Audit · Inspect Trust.
- **States:** Loading (skeleton), Error/Not-found (memory missing/deleted), Editing
  (inline form with validation), Deleting (confirm dialog).
- **Navigation:** → Trust Explorer, → Audit Trail; back to origin.
- **Data Dependencies:** `GET /v1/memories/{id}`, `PATCH`, `DELETE`,
  links to `GET /v1/trust/{id}` and `GET /v1/memories/{id}/audit`.
- **Accessibility:** edit form fields labeled with error text wired to fields;
  destructive delete uses a confirm dialog with clear consequences; provenance
  links are focusable.

### 7.5 Trust Explorer *(first-class screen — see §10)*
- **Purpose:** Visually demonstrate **why a memory is trustworthy and why it was
  retrieved**. The flagship explainability surface.
- **Primary Actions:** View decomposed trust; (when arrived from a search result)
  toggle to the retrieval **ranking-factor** view; open the underlying memory.
- **UI Components:**
  - Confidence gauge (0–1) with band label (Low/Moderate/High).
  - Freshness bar with age + type half-life context ("12 days old · preference
    half-life ~180d").
  - Provenance card: source type → quality mapping, corroborations (+N),
    contradictions (−N).
  - **Explanation** block: the engine's one-sentence rationale, prominent.
  - **Ranking Factors** panel (when from a result): per-signal score bars
    (keyword/vector/metadata/importance/trust) + the weights in effect + the fused
    score — i.e. *why this ranked here*.
  - Source information: links to source/derived_from memories.
- **States:** Loading (skeleton gauges/bars), Error (trust unavailable), Empty
  (no memory selected on the tab → prompt to pick one).
- **Navigation:** → Memory Detail (the subject); back to origin.
- **Data Dependencies:** `GET /v1/trust/{memory_id}`; ranking factors come from the
  originating `POST /v1/retrieval/search` result (`signals`/`weights`/`trust`).
- **Accessibility:** gauges/bars expose numeric values and band labels to TalkBack;
  never rely on color alone for trust bands; explanation is plain text, first in
  reading order.

### 7.6 Settings
- **Purpose:** Configure connection and identity; theme; demo seed.
- **Primary Actions:** Set engine base URL, namespace, actor; test connection;
  choose theme (system/light/dark); load/reset demo seed; (optional) attach proxy
  auth token.
- **UI Components:** form fields with validation; "Test connection" → calls
  `/health`; theme selector; "Load demo scenarios" button; about/version block.
- **States:** Saved (persisted to local storage/DataStore), Validating (connection
  check), Error (unreachable / invalid URL).
- **Navigation:** back to originating screen.
- **Data Dependencies:** `GET /health`; local persistence only otherwise.
- **Accessibility:** every field labeled; connection result announced; theme change
  respects system + reduced-motion.

---

## 8. Domain Models

Mirror the engine exactly (do not extend). Suggested Kotlin shapes:

```kotlin
enum class MemoryType { FACT, EVENT, PREFERENCE, SUMMARY }
enum class MemoryState { CREATED, ACTIVE, CONSOLIDATED, DECAYED, ARCHIVED, DELETED }
enum class ProvenanceSource { USER, INFERRED, CONSOLIDATION, SYSTEM }
enum class RetrievalMode { KEYWORD, VECTOR, HYBRID }

data class Provenance(
    val source: ProvenanceSource,
    val derivedFrom: List<String> = emptyList(),
    val recordedAt: Instant
)

data class Memory(
    val id: String,
    val namespace: String,
    val type: MemoryType,
    val content: String,
    val state: MemoryState,
    val importance: Double,        // 0..1, read-only
    val accessCount: Int,          // read-only
    val metadata: Map<String, Any?> = emptyMap(),
    val provenance: Provenance,
    val createdAt: Instant,
    val updatedAt: Instant,
    val lastAccessedAt: Instant?
)

data class Trust(                  // 0..1 each
    val provenanceQuality: Double,
    val confidence: Double,
    val freshness: Double,
    val explanation: String,
    val inputs: TrustInputs? = null
)

data class TrustInputs(
    val provenanceSource: ProvenanceSource?,
    val corroborations: Int?,
    val contradictions: Int?,
    val ageDays: Int?,
    val typeHalfLifeDays: Int?
)

data class RetrievalSignals(       // any may be absent depending on mode
    val keyword: Double?,
    val vector: Double?,
    val metadata: Double?,
    val importance: Double?,
    val trust: Double?
)

data class SearchResult(
    val memoryId: String,
    val content: String,
    val type: MemoryType,
    val score: Double,             // fused
    val signals: RetrievalSignals,
    val weights: Map<String, Double>,
    val trust: Trust
)

data class AuditEvent(
    val id: String,
    val action: String,            // created | updated | deleted | consolidated | decayed
    val actor: String,
    val at: Instant,
    val diff: Map<String, Any?>
)
```

**Rule:** these are the only domain types. No app-invented entities.

---

## 9. API Contracts

> Base path `/v1`. JSON over HTTP. Timestamps ISO-8601 UTC. Namespace is mandatory.
> Auth is enforced by the deployment proxy — attach the configured credential as an
> opaque header; the app implements **no** login screen of its own.

### Endpoints used by the app

| Method | Path | Used by |
|---|---|---|
| `POST` | `/v1/memories` | Store Memory |
| `GET` | `/v1/memories/{id}` | Memory Detail |
| `PATCH` | `/v1/memories/{id}` | Edit |
| `DELETE` | `/v1/memories/{id}` (`?hard=true`) | Delete |
| `GET` | `/v1/memories?namespace=&type=&state=&limit=&offset=` | Explorer, Dashboard |
| `GET` | `/v1/memories/{id}/audit` | Audit Trail |
| `POST` | `/v1/retrieval/search` | Search |
| `GET` | `/v1/trust/{memory_id}` | Trust Explorer |
| `GET` | `/health`, `/health/ready` | Dashboard, Settings |
| `GET` | `/metrics` | Dashboard SLIs (Prometheus text; parse client-side) |

### Create
```
POST /v1/memories
{ "content": "...", "type": "preference", "namespace": "user:123",
  "metadata": { "source": "settings" }, "provenance": { "source": "user" } }
→ 201  Memory
```

### List
```
GET /v1/memories?namespace=user:123&type=preference&state=active&limit=20&offset=0
→ 200 { "items": [Memory…], "total": 137, "limit": 20, "offset": 0 }
```

### Search (core)
```
POST /v1/retrieval/search
{ "query": "what theme does the user like?", "namespace": "user:123",
  "filters": { "type": "preference", "state": "active" },
  "k": 5, "mode": "hybrid", "min_confidence": 0.0 }
→ 200 {
  "query": "...", "mode": "hybrid",
  "results": [{
    "memory_id": "mem_…", "content": "User prefers dark mode", "type": "preference",
    "score": 0.82,
    "signals": { "keyword": 0.30, "vector": 0.78, "metadata": 1.0,
                 "importance": 0.62, "trust": 0.71 },
    "weights": { "keyword": 0.3, "vector": 0.3, "metadata": 0.1,
                 "importance": 0.1, "trust": 0.2 },
    "trust": { "provenance_quality": 0.9, "confidence": 0.75, "freshness": 0.6,
               "explanation": "User-stated preference (high provenance), corroborated by 2 memories, last confirmed 12 days ago." }
  }]
}
```

### Trust
```
GET /v1/trust/{memory_id}
→ 200 { "memory_id": "mem_…", "provenance_quality": 0.9, "confidence": 0.75,
        "freshness": 0.6, "explanation": "...",
        "inputs": { "provenance_source": "user", "corroborations": 2,
                    "contradictions": 0, "age_days": 12, "type_half_life_days": 180 } }
```

### Audit
```
GET /v1/memories/{id}/audit
→ 200 { "items": [ { "id": "evt_…", "action": "updated", "actor": "user:123",
                     "at": "...", "diff": { "content": ["old","new"] } } ] }
```

### Errors
```
{ "error": { "code": "not_found", "message": "memory not found", "details": {} } }
```
Status codes: 200/201/204 success · 400/422 validation · 401/403 auth · 404 ·
409 conflict · 500 server. Map each to a friendly, actionable UI message (§12).

**Guarantees you can rely on:** every search result carries `signals` **and**
`trust`; the trust shape is stable; soft-delete is default and audit always
persists.

---

## 10. Trust Model (Trust Explorer is first-class)

Trust travels with every result and is **fully decomposable** — render it, never
hide it.

**The four signals (each 0..1):**
- **Provenance quality** — source mapping: `user`/explicit **1.0** →
  `consolidation` **0.75** → `inferred` **0.5** → `system` **0.4** (unknown 0.5).
- **Confidence** — provenance floor, raised toward 1.0 by **corroboration**
  (multiple memories agree, saturating), reduced a fixed penalty per
  **contradiction**.
- **Freshness** — type-aware exponential decay; `preference` ages slowly (~180d
  half-life) vs `event` fast (~14d). Stale ⇒ down-weighted, **never deleted**.
- **Explanation** — one human-readable sentence the engine returns; show it
  prominently.

**Ranking factors (why it was retrieved):** the search result's `signals` +
`weights` + fused `score`. Trust enters ranking fusion as a weighted dimension
(default weight ~0.2). The Trust Explorer must visually connect *trust* and
*ranking*: "this scored 0.82 because vector=0.78 (w .3), trust=0.71 (w .2), …".

**UX requirements:**
- A **confidence gauge** with band labels (Low <0.4 / Moderate 0.4–0.7 / High >0.7).
- **Freshness** shown with concrete age + half-life context.
- **Provenance** shown as source + corroboration/contradiction counts.
- **Per-signal score bars** for ranking factors with numeric values and weights.
- Color encodes band but is **always paired with text** (accessibility).

**Stable-contract note:** corroboration/contradiction are lexical stand-ins today
and may become NLI later — the **response shape will not change**, so the UI is
forward-compatible.

---

## 11. State Management

- **Single source of truth:** repositories own data; ViewModels expose immutable UI
  state via `StateFlow<UiState>`; Compose screens render state and emit events only.
- **UiState pattern** per screen:
  ```kotlin
  sealed interface UiState<out T> {
    data object Loading : UiState<Nothing>
    data class Empty(val reason: EmptyReason) : UiState<Nothing>
    data class Error(val message: String, val retry: (() -> Unit)?) : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
  }
  ```
  Distinguish **Empty** (no data exists) from **No-results** (query ran, matched
  nothing) — Search needs both.
- **Caching:** repositories cache last successful results in memory; offline mode
  (§16) serves last-known data with a clear "stale" indicator.
- **Settings** (base URL, namespace, actor, theme, optional token) persisted via
  **DataStore**; injected into the HTTP layer.
- **No business logic in ViewModels beyond orchestration** — scoring/ranking/trust
  come from the engine.
- Events (store/edit/delete) are one-shot (`Channel`/`SharedFlow`) → snackbars,
  navigation.

---

## 12. Error Handling

| Condition | UI behavior |
|---|---|
| Engine unreachable / DNS / timeout | Full-screen Error on Dashboard; inline banner elsewhere; **Retry** + **Open Settings** |
| 401/403 (proxy auth) | "Not authorized — check your access token in Settings" |
| 404 (memory gone/deleted) | Detail shows "This memory no longer exists" → back to Explore |
| 400/422 (validation) | Inline field errors on forms; never a raw stack trace |
| 409 (conflict) | "This memory changed since you opened it — reload" |
| 500 / unknown | "Something went wrong on the engine — try again"; log details, show friendly text |
| No search results | Distinct No-results state with suggestions (broaden query, lower min-confidence, switch mode) |
| Offline | Serve cached data + "Offline — showing last known" badge; queue nothing destructive |

Rules: **never** surface technical/JSON errors to users; every error is
**actionable** (retry or a next step); destructive actions confirm first.

---

## 13. Accessibility

Target **WCAG AA**; Android specifics:
- **TalkBack:** every interactive element and data viz (score bars, gauges) has a
  meaningful `contentDescription`; lists expose item position/count.
- **Color independence:** trust bands and memory states always pair color with a
  text label / icon (no color-only meaning).
- **Contrast:** AA contrast in both themes; verify semantic trust/state colors.
- **Touch targets:** ≥ 48dp; adequate spacing.
- **Dynamic type / font scaling:** layouts reflow to 200% font scale without
  clipping.
- **Focus order:** logical reading order; explanation text first in Trust Explorer.
- **Reduced motion:** honor system "remove animations"; keep motion purposeful and
  non-blocking.
- **Forms:** labels tied to fields; error text programmatically associated.
- **Keyboard / switch access:** full operability without touch.

---

## 14. Design System

**Feel like a mobile Admin Console.** Inspiration: **Linear · Stripe · Material 3**
— dense but calm, information-rich, restrained color, premium and professional.
Priorities: **Trust · Clarity · Professionalism · Explainability.**

- **Typography:** **Inter** (or Material 3 type scale mapped to Inter). Clear
  hierarchy; numerals legible for scores.
- **Layout:** **8-point grid**; generous whitespace; content-first; cards for
  grouped signals.
- **Themes:** **Light and Dark, first-class** (follow system by default).
- **Color:** neutral base + restrained accent. **Semantic colors:**
  - *Trust bands:* High = green, Moderate = amber, Low = red (always with text).
  - *Memory states:* active (neutral/blue), consolidated (purple), decayed
    (muted/grey), archived (grey), deleted (red/strikethrough).
- **Motion:** subtle, purposeful, never blocking; respect reduced-motion.
- **Signature primitive — Score Bar:** a reusable horizontal bar with label +
  numeric value (0–1), used everywhere explainability appears (search signals,
  trust dimensions, importance). This is the visual backbone, mirroring the web
  console's score-bar primitive. Build it once, reuse it.
- **Components:** Material 3 (`Card`, `NavigationBar`, `FilledTonalButton`,
  `AssistChip`/`FilterChip`, `LinearProgressIndicator` styled as score bars,
  `TopAppBar`, `ModalBottomSheet` for Store Memory).
- **Badges:** type and state badges as compact chips with text.

---

## 15. Android Architecture

Recommended, idiomatic, and required to keep the app a *thin faithful client*:

- **UI:** **Jetpack Compose** + **Material 3**.
- **Pattern:** **MVVM** — Compose screens → ViewModel (`StateFlow` UiState) →
  Repository → API.
- **Repository pattern:** one repository per concern (`MemoryRepository`,
  `RetrievalRepository`, `TrustRepository`, `HealthRepository`) as the **single
  source of truth**; they own caching and map DTO→domain.
- **DI:** **Hilt** — provide HTTP client, repositories, Settings store.
- **Navigation:** **Navigation Compose** with typed routes (`memoryId`, `query`).
- **Async:** **Coroutines** + **Flow**; `StateFlow` for UI state, `Flow` for
  streams, suspend functions for one-shot calls.
- **Networking:** Retrofit + OkHttp + kotlinx-serialization/Moshi (or Ktor client).
  A single configurable `BaseUrl` + auth-header interceptor (token from Settings).
  A small `/metrics` text parser (Prometheus exposition → counters/quantiles) lives
  in a pure, unit-tested util.
- **Persistence:** **DataStore** for settings; optional **Room** for offline cache
  of last-known memories/results (§16).
- **Layering rules:**
  - **No business logic in screens** (no scoring/ranking/trust math anywhere in the
    app — render engine output).
  - **No duplicated memory logic** — the engine is authoritative.
  - DTOs at the network edge; domain models (§8) everywhere else.
- **Testing:** ViewModel unit tests over fake repositories; repository tests over a
  mock web server; pure-function tests for the `/metrics` parser and any formatting.
- **Module sketch:**
  ```
  :app        — Compose UI, navigation, ViewModels, DI wiring
  :core-domain— domain models (§8), repository interfaces
  :core-data  — Retrofit DTOs, repository impls, metrics parser, DataStore/Room
  :core-ui    — design system: theme, ScoreBar, badges, state scaffolds
  ```
  (A single well-structured module is acceptable for a reference app; keep the
  boundaries above as packages if not modules.)

---

## 16. Offline Mode

This is a **reference/demo** app, so offline is about graceful degradation, not a
full local engine:

- **Read resilience:** repositories cache the last successful Dashboard counts,
  Explorer pages, search results, and opened memories. When offline, serve cached
  data with a clear **"Offline — showing last known"** badge.
- **No destructive writes offline:** Store/Edit/Delete require connectivity;
  disable their actions with an explanatory state when offline (do **not** silently
  queue governance actions).
- **Connection awareness:** observe connectivity; surface a persistent but
  unobtrusive offline indicator; auto-retry health on reconnect.
- **Demo seed availability:** the seeded scenarios (§17) load from the engine; once
  fetched they remain inspectable offline via cache.
- *(Optional, clearly labeled)* an "on-device only" toggle is **out of scope** for
  this reference unless the engine exposes a local mode — do not invent one.

---

## 17. Demo Scenarios

Ship a **"Load demo scenarios"** action (Settings) that stores these via
`POST /v1/memories`, then guides the user to the matching query. Each is realistic
and exercises a different signal mix. (≥10 below.)

| # | Stored Memory (type) | Retrieval Query | Expected Result | Trust Information |
|---|---|---|---|---|
| 1 | "User wants to become a staff engineer within 2 years" *(preference)* | "what are the user's career goals?" | The career-goal memory ranks #1 | High provenance (user-stated 0.9), confidence ~0.7, slow-aging preference (fresh) |
| 2 | "Idea: an offline-first journaling app with semantic search" *(fact)* | "what project ideas has the user had?" | The project-idea memory surfaces | Provenance 0.9; freshness depends on age; explanation cites user source |
| 3 | "Flight to Tokyo cost ¥82,000 on 2026-05-12" *(event)* | "how much did the Tokyo flight cost?" | Travel receipt event returns with strong keyword+vector | Event freshness decays fast (~14d half-life) — show down-weighting |
| 4 | "Standup decision: adopt Qdrant for vector search" *(event)* | "what did we decide about vector search?" | Meeting/engineering decision returns | Confidence raised if corroborated by a second decision memory |
| 5 | "Engineering decision: SQLite for MVP, Postgres at scale" *(fact)* | "which database are we using?" | The DB-decision fact ranks high | Provenance 0.9; explanation: user-stated, corroborated |
| 6 | "Learning note: BM25 saturates term frequency via k1" *(fact)* | "how does BM25 handle term frequency?" | Learning note returns on strong vector match | Moderate confidence; fresh; high vector signal |
| 7 | "User prefers dark mode" *(preference)* + "User switched to light mode" *(preference, later)* | "what theme does the user prefer?" | Latest preference ranks higher; older one shows as contradicted/decaying | **Contradiction** lowers confidence on the stale one — demonstrate the penalty |
| 8 | "User upgraded to Pro plan on 2026-06-01" *(event)* | "is the user a paying customer?" | Upgrade event returns | Fresh event, high freshness; provenance user/system |
| 9 | "Meeting note: ship Android reference app after Phase 7" *(event)* | "what's next after the admin console?" | Roadmap meeting note returns | Confidence moderate; freshness moderate |
| 10 | Consolidated summary derived from #1, #9 *(summary)* | "summarize the user's goals and plans" | The **summary** memory returns, linking sources | Provenance 0.75 (consolidation); `derived_from` shows source memories |
| 11 | "User's timezone is IST" *(fact)* | "what timezone is the user in?" | Stable fact returns with high metadata+keyword | High provenance, very fresh (stable fact), high confidence |
| 12 | "User mentioned disliking long meetings" *(preference)* | "how does the user feel about meetings?" | Preference returns | Inferred-vs-user provenance affects quality; explanation states the source |

These cover: career goals, project ideas, travel receipts, meeting notes,
engineering decisions, learning notes, contradiction handling, consolidation/summary
provenance, and freshness decay — the full trust/retrieval story.

---

## 18. Acceptance Criteria

The app is done when **all** hold:

1. **All six screens** (Dashboard, Search, Explorer, Memory Detail, Trust Explorer,
   Settings) implemented with **Empty / Loading / Error** (and Search's distinct
   **No-results**) states.
2. **Store → Search → Inspect → Trust** end-to-end works against a live engine using
   only the §9 contracts.
3. **Every search result renders `signals` + `weights` + `trust`** via the shared
   **Score Bar** primitive — explainability is visual, not textual-only.
4. **Trust Explorer** shows confidence (gauge + band), freshness (age + half-life),
   provenance (source + corroboration/contradiction), the explanation, and the
   ranking-factor breakdown.
5. **Soft-delete** removes a memory from default retrieval while its **audit trail
   persists** and is viewable.
6. **Light + dark themes** both ship; **WCAG AA** met (contrast, TalkBack, 48dp
   targets, 200% font scale, reduced-motion, color+text encoding).
7. **No business logic in the app** — no scoring/ranking/trust computation; all
   values come from the engine.
8. **Settings** configures base URL / namespace / actor / theme (+ optional auth
   token), persisted; "Test connection" works.
9. **Demo seed** (§17) loads and each scenario's query returns the expected memory
   with sensible trust.
10. **Architecture:** Compose + M3 + MVVM + Repository + Hilt + Navigation Compose +
    Coroutines/Flow, single source of truth; ViewModel and metrics-parser unit
    tests pass.
11. **Resilience:** offline serves cached reads with a clear indicator; destructive
    writes are disabled offline; all errors are friendly and actionable.

---

## 19. Non-Goals

- **Not a chatbot.** No conversational assistant, no LLM chat UI.
- **Not a note-taking app.** Memories are demonstration data, not a personal
  notebook product.
- **Not a task manager / productivity app.**
- **No bespoke login/auth UI** — auth is enforced by the deployment proxy; the app
  only attaches a configured credential. (No user registration, password, or
  session screens.)
- **No new APIs, domain models, trust models, or memory models** — reuse §8–§10.
- **No re-implementation of engine intelligence** (scoring, ranking, trust math,
  embedding, dedup, consolidation, decay) on-device.
- **No historical trend charts / analytics dashboards** beyond the simple live SLIs
  on Dashboard (those belong to Grafana, not this app).
- **No multi-tenant admin / user management.**

---

## 20. Claude Design Instructions

When you (Claude Design) implement this app:

1. **Treat §9 contracts as fixed.** Build a typed network layer and domain models
   (§8) exactly as specified. If a field is missing at runtime, degrade gracefully —
   do not invent fields.
2. **Build the Score Bar primitive first** (§14) — it is reused across Search and
   Trust Explorer; it is the explainability backbone.
3. **Implement the state scaffold early** (Loading/Empty/Error/No-results, §11/§13)
   and reuse it on every screen — no screen ships without all states.
4. **Wire the happy path J1** ("Can I trust this?", §5) before polishing — it's the
   demo's spine: Dashboard → Search → result with signal bars → Memory Detail →
   Trust Explorer.
5. **Keep the app thin.** Any temptation to compute a score, rank, or trust value
   on-device is a bug — render what the engine returns.
6. **Match the console's visual language** (§14): Inter, 8-pt grid, light+dark,
   restrained semantic color, Material 3. It should read as the mobile sibling of
   the web Admin Console.
7. **Make explainability the star.** Every result and every memory should let the
   user reach *why* in one tap.
8. **Ship the demo seed** (§17) and verify each scenario's query/trust outcome.
9. **Accessibility is acceptance, not polish** (§13) — TalkBack, contrast, font
   scaling, color+text encoding from the start.
10. **Deliverable:** a runnable Android app (Compose/M3/MVVM/Hilt/Navigation
    Compose/Coroutines) that satisfies every item in §18, integrating only with the
    SCP Memory Engine HTTP API in §9. Produce code, structure, and a short README
    on configuring the engine base URL and loading the demo seed.

> Configuration you can assume the operator provides: an engine **base URL**, a
> **namespace**, an **actor** identifier, and (optionally) a proxy **auth token** —
> all entered in Settings. Nothing else is required to run.
