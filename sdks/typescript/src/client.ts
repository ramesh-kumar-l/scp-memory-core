/**
 * The SCP Memory Engine client — a facade over the four resource groups.
 *
 *   import { SCPMemoryClient } from "@scp/memory-sdk";
 *
 *   const client = new SCPMemoryClient({ baseUrl: "http://localhost:8000", actor: "alice" });
 *   const mem = await client.memories.create({
 *     content: "user prefers dark mode", namespace: "user:1",
 *     type: "preference", source: "settings",
 *   });
 *   const hits = await client.retrieval.search({ query: "theme?", namespace: "user:1" });
 *   const verdict = await client.trust.explain(mem.id, "user:1");
 */

import { HttpClient, type HttpClientOptions } from "./http.js";
import { IntelligenceResource } from "./resources/intelligence.js";
import { MemoriesResource } from "./resources/memories.js";
import { RetrievalResource } from "./resources/retrieval.js";
import { TrustResource } from "./resources/trust.js";

export class SCPMemoryClient {
  readonly memories: MemoriesResource;
  readonly intelligence: IntelligenceResource;
  readonly retrieval: RetrievalResource;
  readonly trust: TrustResource;
  private readonly http: HttpClient;

  constructor(options: HttpClientOptions) {
    this.http = new HttpClient(options);
    this.memories = new MemoriesResource(this.http);
    this.intelligence = new IntelligenceResource(this.http);
    this.retrieval = new RetrievalResource(this.http);
    this.trust = new TrustResource(this.http);
  }

  /** Liveness probe (GET /health). */
  health(): Promise<{ status: string }> {
    return this.http.request<{ status: string }>("GET", "/health");
  }
}
