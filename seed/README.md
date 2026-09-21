# seed/ — Golden Examples seeder (engine)

Loads the 10 Golden Examples from [`../documents/golden-examples.json`](../documents/golden-examples.json)
and creates them in the engine through the **HTTP API** (the same contract any client
uses), then prints a verification summary. The dataset is shared with the Android seeder
(`SCPMemoryEngine_AndroidReferenceApp/seed/seed_golden_device.py`).

## Run

```bash
# Option A — against a running engine (so the Admin Console can view the data)
python -m scp_memory                          # starts on http://localhost:8000
python seed/seed_golden_examples.py           # --base-url http://localhost:8000

# Option B — quick check, no server (in-process TestClient + the engine's SQLite file)
python seed/seed_golden_examples.py --in-process

# Remove the seeded memories
python seed/seed_golden_examples.py --reset            # add --in-process if you used it
```

No third-party dependencies in HTTP mode (stdlib `urllib` only). `--in-process` needs the
engine installed (`pip install -e .`).

## Verify

The script prints the created count and a trust-scored sample search. You can also:

```bash
curl 'http://localhost:8000/v1/memories?namespace=demo:golden'      # expect 10 items
```

…or open the **Admin Console → Memory Explorer** and set the namespace to `demo:golden`.

## What each example demonstrates

See [`../documents/11-demo-and-examples-pack.md`](../documents/11-demo-and-examples-pack.md)
for the full table (provenance spectrum, contradiction, consolidation, freshness/decay,
metadata + hybrid retrieval across the three golden use cases).

## Engine vs device: an honest note

The create API is the public contract — it sets `recorded_at = now` and owns `importance`,
the memory `id`, and `derived_from`. So on the engine path the **freshness/decay** effect is
muted (everything is fresh) and the default `HashingEmbedder` is a hermetic stand-in, so
exact ranking is approximate. The **trust scores** (provenance/confidence) are fully
meaningful here. To see freshness-driven ranking and `derived_from`, use the Android seeder
(direct Room write, backdated ages) or set `SCP_EMBEDDER=sentence-transformers`.
