/* A focused Prometheus text-exposition parser plus the aggregations the Dashboard
   and Benchmarks screens need: counter sums and histogram quantiles. Pure and
   unit-tested (no DOM, no fetch) so the SLO math is verifiable. */

export interface Sample {
  name: string;
  labels: Record<string, string>;
  value: number;
}

const LINE = /^(\w+)(\{([^}]*)\})?\s+([^\s]+)/;

export function parseMetrics(text: string): Sample[] {
  const out: Sample[] = [];
  for (const raw of text.split("\n")) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const m = LINE.exec(line);
    if (!m) continue;
    const value = Number(m[4]);
    if (!Number.isFinite(value)) continue;
    out.push({ name: m[1]!, labels: parseLabels(m[3]), value });
  }
  return out;
}

function parseLabels(body: string | undefined): Record<string, string> {
  const labels: Record<string, string> = {};
  if (!body) return labels;
  const re = /(\w+)="((?:[^"\\]|\\.)*)"/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(body))) {
    labels[m[1]!] = m[2]!.replace(/\\"/g, '"').replace(/\\\\/g, "\\");
  }
  return labels;
}

/** Sum a counter across all label sets, optionally filtered by labels. */
export function counterSum(
  samples: Sample[],
  name: string,
  where: Record<string, string> = {},
): number {
  return samples
    .filter((s) => s.name === name && matches(s.labels, where))
    .reduce((acc, s) => acc + s.value, 0);
}

/** Group a counter's total by one label (e.g. retrieval queries by mode). */
export function counterByLabel(
  samples: Sample[],
  name: string,
  label: string,
): Record<string, number> {
  const out: Record<string, number> = {};
  for (const s of samples) {
    if (s.name !== name) continue;
    const key = s.labels[label] ?? "unknown";
    out[key] = (out[key] ?? 0) + s.value;
  }
  return out;
}

function matches(labels: Record<string, string>, where: Record<string, string>): boolean {
  return Object.entries(where).every(([k, v]) => labels[k] === v);
}

export interface LatencySummary {
  count: number;
  p50: number;
  p95: number;
  p99: number;
}

/**
 * Quantiles from a histogram's `_bucket` series (seconds → milliseconds),
 * aggregating bucket counts across label sets matching `where`. Mirrors
 * Prometheus `histogram_quantile` with linear interpolation inside the bucket.
 */
export function latencyMs(
  samples: Sample[],
  metric: string,
  where: Record<string, string> = {},
): LatencySummary {
  const buckets = new Map<number, number>();
  for (const s of samples) {
    if (s.name !== `${metric}_bucket`) continue;
    if (!matches(s.labels, where)) continue;
    const le = s.labels.le === "+Inf" ? Infinity : Number(s.labels.le);
    if (Number.isNaN(le)) continue;
    buckets.set(le, (buckets.get(le) ?? 0) + s.value);
  }
  const edges = [...buckets.keys()].sort((a, b) => a - b);
  const total = buckets.get(Infinity) ?? (edges.length ? buckets.get(edges[edges.length - 1]!)! : 0);
  const quantile = (q: number): number => {
    if (total === 0) return 0;
    const target = q * total;
    let lowerEdge = 0;
    let lowerCount = 0;
    for (const edge of edges) {
      const cumulative = buckets.get(edge)!;
      if (cumulative >= target) {
        if (!Number.isFinite(edge)) return lowerEdge * 1000;
        const span = edge - lowerEdge;
        const within = cumulative - lowerCount;
        const frac = within > 0 ? (target - lowerCount) / within : 0;
        return (lowerEdge + span * frac) * 1000;
      }
      lowerEdge = edge;
      lowerCount = cumulative;
    }
    return lowerEdge * 1000;
  };
  return { count: total, p50: quantile(0.5), p95: quantile(0.95), p99: quantile(0.99) };
}

/** Non-2xx/3xx fraction over the request histogram's `_count` series. */
export function errorRatio(samples: Sample[], metric: string): number {
  let total = 0;
  let errors = 0;
  for (const s of samples) {
    if (s.name !== `${metric}_count`) continue;
    total += s.value;
    if (Number(s.labels.status) >= 500) errors += s.value;
  }
  return total === 0 ? 0 : errors / total;
}
