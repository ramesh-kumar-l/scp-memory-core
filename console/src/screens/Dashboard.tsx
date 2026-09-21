/* Dashboard — system health + memory/retrieval/trust at a glance, computed from
   the engine's /health/ready and /metrics. Latency tiles are checked against the
   Phase-6 SLOs (p95<300ms, p99<1s). */

import { PageHead } from "../components/PageHead";
import { Badge } from "../components/Badge";
import { ErrorState, Loading } from "../components/States";
import { useMetrics, useReady } from "../api/queries";
import { counterByLabel, counterSum, errorRatio, latencyMs } from "../api/metrics";
import type { Sample } from "../api/metrics";

const REQ = "scp_api_request_duration_seconds";

function Stat({ label, value, tone }: { label: string; value: string; tone?: string }) {
  return (
    <div className="card card--pad">
      <div className="stat__label">{label}</div>
      <div className="stat__value" style={tone ? { color: `var(--${tone})` } : undefined}>
        {value}
      </div>
    </div>
  );
}

export function Dashboard() {
  const ready = useReady();
  const metrics = useMetrics();

  return (
    <>
      <PageHead title="Dashboard" subtitle="Live system health and memory signals" />
      <div className="stack">
        <Health
          live={!metrics.isError}
          ready={ready.data?.ok ?? null}
          db={ready.data?.database}
        />
        {metrics.isLoading ? (
          <Loading rows={4} label="Loading metrics" />
        ) : metrics.isError ? (
          <ErrorState error={metrics.error} onRetry={() => metrics.refetch()} />
        ) : (
          <Tiles samples={metrics.data ?? []} />
        )}
      </div>
    </>
  );
}

function Health({ live, ready, db }: { live: boolean; ready: boolean | null; db?: string }) {
  return (
    <div className="card card--pad row" style={{ gap: "var(--space-4)" }}>
      <strong>Engine</strong>
      <Badge tone={live ? "ok" : "danger"}>{live ? "live" : "unreachable"}</Badge>
      <Badge tone={ready === null ? "neutral" : ready ? "ok" : "danger"}>
        {ready === null ? "readiness unknown" : ready ? "ready" : "not ready"}
      </Badge>
      {db && <span className="stat__label">database: {db}</span>}
    </div>
  );
}

function Tiles({ samples }: { samples: Sample[] }) {
  const lat = latencyMs(samples, REQ);
  const errPct = errorRatio(samples, REQ) * 100;
  const modes = counterByLabel(samples, "scp_retrieval_queries_total", "mode");
  const modeStr =
    Object.entries(modes)
      .map(([m, n]) => `${m}:${n}`)
      .join("  ") || "—";

  return (
    <div className="stack">
      <section>
        <h2 className="page-sub" style={{ marginBottom: "var(--space-2)" }}>
          Memory
        </h2>
        <div className="grid grid--stats">
          <Stat label="Created" value={fmt(counterSum(samples, "scp_memories_created_total"))} />
          <Stat label="Updated" value={fmt(counterSum(samples, "scp_memories_updated_total"))} />
          <Stat label="Deleted" value={fmt(counterSum(samples, "scp_memories_deleted_total"))} />
          <Stat label="Decayed" value={fmt(counterSum(samples, "scp_memories_decayed_total"))} />
          <Stat label="Deduped" value={fmt(counterSum(samples, "scp_memories_deduped_total"))} />
          <Stat
            label="Consolidated"
            value={fmt(counterSum(samples, "scp_memories_consolidated_total"))}
          />
        </div>
      </section>

      <section>
        <h2 className="page-sub" style={{ marginBottom: "var(--space-2)" }}>
          Retrieval &amp; Trust
        </h2>
        <div className="grid grid--stats">
          <Stat label="Retrieval queries" value={modeStr} />
          <Stat
            label="Trust evaluations"
            value={fmt(counterSum(samples, "scp_trust_evaluations_total"))}
          />
        </div>
      </section>

      <section>
        <h2 className="page-sub" style={{ marginBottom: "var(--space-2)" }}>
          API (SLO)
        </h2>
        <div className="grid grid--stats">
          <Stat label="Requests" value={fmt(lat.count)} />
          <Stat label="Error rate" value={`${errPct.toFixed(2)}%`} tone={errPct > 0.1 ? "danger" : "ok"} />
          <Stat label="p50 latency" value={`${lat.p50.toFixed(0)} ms`} />
          <Stat
            label="p95 latency"
            value={`${lat.p95.toFixed(0)} ms`}
            tone={lat.p95 > 300 ? "warn" : "ok"}
          />
          <Stat
            label="p99 latency"
            value={`${lat.p99.toFixed(0)} ms`}
            tone={lat.p99 > 1000 ? "warn" : "ok"}
          />
        </div>
      </section>
    </div>
  );
}

function fmt(n: number): string {
  return Number.isInteger(n) ? n.toLocaleString() : n.toFixed(2);
}
