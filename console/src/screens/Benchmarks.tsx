/* Benchmarks — per-endpoint latency percentiles derived live from the request
   histogram, checked against the Phase-6 SLOs (21-benchmark-results). The
   retrieval-search row carries its own 500ms p95 target. */

import { PageHead } from "../components/PageHead";
import { Badge } from "../components/Badge";
import { ErrorState, Loading } from "../components/States";
import { useMetrics } from "../api/queries";
import { latencyMs, type Sample } from "../api/metrics";

const REQ = "scp_api_request_duration_seconds";
const RETRIEVAL = "/v1/retrieval/search";

interface Row {
  endpoint: string;
  count: number;
  p50: number;
  p95: number;
  p99: number;
  p95Target: number;
}

function rows(samples: Sample[]): Row[] {
  const endpoints = new Set<string>();
  for (const s of samples) {
    if (s.name === `${REQ}_count` && s.labels.endpoint) endpoints.add(s.labels.endpoint);
  }
  return [...endpoints]
    .map((endpoint) => {
      const l = latencyMs(samples, REQ, { endpoint });
      return {
        endpoint,
        count: l.count,
        p50: l.p50,
        p95: l.p95,
        p99: l.p99,
        p95Target: endpoint === RETRIEVAL ? 500 : 300,
      };
    })
    .sort((a, b) => b.count - a.count);
}

export function Benchmarks() {
  const metrics = useMetrics();

  return (
    <>
      <PageHead title="Benchmarks" subtitle="Live latency percentiles vs SLO targets" />
      {metrics.isLoading ? (
        <Loading label="Loading metrics" />
      ) : metrics.isError ? (
        <ErrorState error={metrics.error} onRetry={() => metrics.refetch()} />
      ) : (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Endpoint</th>
                <th>Requests</th>
                <th>p50</th>
                <th>p95</th>
                <th>p99</th>
                <th>SLO (p95)</th>
              </tr>
            </thead>
            <tbody>
              {rows(metrics.data ?? []).map((r) => (
                <tr key={r.endpoint} style={{ cursor: "default" }}>
                  <td className="mono">{r.endpoint}</td>
                  <td>{r.count.toLocaleString()}</td>
                  <td>{r.p50.toFixed(0)} ms</td>
                  <td>{r.p95.toFixed(0)} ms</td>
                  <td>{r.p99.toFixed(0)} ms</td>
                  <td>
                    <Badge tone={r.p95 <= r.p95Target ? "ok" : "danger"}>
                      {r.p95 <= r.p95Target ? "met" : "breached"} · &lt;{r.p95Target}ms
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
