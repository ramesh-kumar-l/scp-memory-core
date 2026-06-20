/** Hybrid retrieval (POST /v1/retrieval/search) — explainable, trust-aware. */

import type { HttpClient } from "../http.js";
import type { SearchParams, SearchResponse } from "../types.js";

export class RetrievalResource {
  constructor(private readonly http: HttpClient) {}

  search(params: SearchParams): Promise<SearchResponse> {
    const { query, namespace, k = 10, mode = "hybrid", type, state, minConfidence } = params;
    const body: Record<string, unknown> = { query, namespace, k, mode };
    if (type !== undefined) body.type = type;
    if (state !== undefined) body.state = state;
    if (minConfidence !== undefined) body.min_confidence = minConfidence;
    return this.http.request<SearchResponse>("POST", "/v1/retrieval/search", { body });
  }
}
