/** Trust explainability (GET /v1/trust/{memory_id}). */

import type { HttpClient } from "../http.js";
import type { TrustBreakdown } from "../types.js";

export class TrustResource {
  constructor(private readonly http: HttpClient) {}

  explain(memoryId: string, namespace: string): Promise<TrustBreakdown> {
    return this.http.request<TrustBreakdown>(
      "GET",
      `/v1/trust/${encodeURIComponent(memoryId)}`,
      { params: { namespace } },
    );
  }
}
