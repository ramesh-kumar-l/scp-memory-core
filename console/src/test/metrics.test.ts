import { describe, expect, it } from "vitest";
import {
  counterByLabel,
  counterSum,
  errorRatio,
  latencyMs,
  parseMetrics,
} from "../api/metrics";

const SAMPLE = `
# HELP scp_memories_created_total Memories created.
# TYPE scp_memories_created_total counter
scp_memories_created_total 7.0
scp_retrieval_queries_total{mode="hybrid"} 3.0
scp_retrieval_queries_total{mode="keyword"} 2.0
scp_api_request_duration_seconds_bucket{endpoint="/v1/memories",status="200",le="0.05"} 0
scp_api_request_duration_seconds_bucket{endpoint="/v1/memories",status="200",le="0.1"} 8
scp_api_request_duration_seconds_bucket{endpoint="/v1/memories",status="200",le="0.25"} 10
scp_api_request_duration_seconds_bucket{endpoint="/v1/memories",status="200",le="+Inf"} 10
scp_api_request_duration_seconds_count{endpoint="/v1/memories",status="200"} 10
scp_api_request_duration_seconds_count{endpoint="/v1/memories",status="500"} 2
`;

describe("metrics parser", () => {
  const samples = parseMetrics(SAMPLE);

  it("ignores comments and parses labels + values", () => {
    expect(counterSum(samples, "scp_memories_created_total")).toBe(7);
  });

  it("sums a labelled counter and groups by label", () => {
    expect(counterSum(samples, "scp_retrieval_queries_total")).toBe(5);
    expect(counterByLabel(samples, "scp_retrieval_queries_total", "mode")).toEqual({
      hybrid: 3,
      keyword: 2,
    });
  });

  it("computes histogram quantiles in ms via interpolation", () => {
    const l = latencyMs(samples, "scp_api_request_duration_seconds");
    expect(l.count).toBe(10);
    // p50 (target 5) falls in the 0.05–0.1 bucket: 0.05 + 0.05*(5/8) = 0.08125s
    expect(l.p50).toBeCloseTo(81.25, 1);
    // p95 (target 9.5) falls in 0.1–0.25 bucket
    expect(l.p95).toBeGreaterThan(100);
    expect(l.p95).toBeLessThan(250);
  });

  it("derives the 5xx error ratio from _count series", () => {
    expect(errorRatio(samples, "scp_api_request_duration_seconds")).toBeCloseTo(2 / 12, 5);
  });
});
