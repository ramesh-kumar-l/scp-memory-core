/** Memory self-management passes (POST /v1/intelligence/{decay,dedup,consolidate}). */

import type { HttpClient } from "../http.js";
import type { ConsolidateResult, DecayResult, DedupResult } from "../types.js";

export class IntelligenceResource {
  constructor(private readonly http: HttpClient) {}

  decay(namespace: string, threshold?: number): Promise<DecayResult> {
    const body: Record<string, unknown> = { namespace };
    if (threshold !== undefined) body.threshold = threshold;
    return this.http.request<DecayResult>("POST", "/v1/intelligence/decay", { body });
  }

  dedup(namespace: string, threshold?: number): Promise<DedupResult> {
    const body: Record<string, unknown> = { namespace };
    if (threshold !== undefined) body.threshold = threshold;
    return this.http.request<DedupResult>("POST", "/v1/intelligence/dedup", { body });
  }

  consolidate(
    namespace: string,
    sourceIds: string[],
    summary?: string,
  ): Promise<ConsolidateResult> {
    const body: Record<string, unknown> = { namespace, source_ids: sourceIds };
    if (summary !== undefined) body.summary = summary;
    return this.http.request<ConsolidateResult>("POST", "/v1/intelligence/consolidate", { body });
  }
}
