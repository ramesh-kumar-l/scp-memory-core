/** Memory CRUD + audit (POST/GET/PATCH/DELETE /v1/memories, .../audit). */

import type { HttpClient } from "../http.js";
import type {
  AuditLog,
  CreateMemoryParams,
  ListMemoriesParams,
  Memory,
  MemoryPage,
  UpdateMemoryParams,
} from "../types.js";

export class MemoriesResource {
  constructor(private readonly http: HttpClient) {}

  create(params: CreateMemoryParams): Promise<Memory> {
    const { namespace, content, type = "fact", metadata, source } = params;
    const body: Record<string, unknown> = { content, namespace, type };
    if (metadata !== undefined) body.metadata = metadata;
    if (source !== undefined) body.source = source;
    return this.http.request<Memory>("POST", "/v1/memories", { body });
  }

  get(memoryId: string, namespace?: string): Promise<Memory> {
    return this.http.request<Memory>("GET", `/v1/memories/${encodeURIComponent(memoryId)}`, {
      params: { namespace },
    });
  }

  update(memoryId: string, params: UpdateMemoryParams): Promise<Memory> {
    const { namespace, ...rest } = params;
    const body: Record<string, unknown> = {};
    if (rest.content !== undefined) body.content = rest.content;
    if (rest.type !== undefined) body.type = rest.type;
    if (rest.metadata !== undefined) body.metadata = rest.metadata;
    return this.http.request<Memory>("PATCH", `/v1/memories/${encodeURIComponent(memoryId)}`, {
      params: { namespace },
      body,
    });
  }

  async delete(memoryId: string, opts: { hard?: boolean; namespace?: string } = {}): Promise<void> {
    await this.http.request<void>("DELETE", `/v1/memories/${encodeURIComponent(memoryId)}`, {
      params: { hard: opts.hard ?? false, namespace: opts.namespace },
    });
  }

  list(params: ListMemoriesParams): Promise<MemoryPage> {
    const { namespace, type, state, limit = 50, offset = 0 } = params;
    return this.http.request<MemoryPage>("GET", "/v1/memories", {
      params: { namespace, type, state, limit, offset },
    });
  }

  audit(memoryId: string): Promise<AuditLog> {
    return this.http.request<AuditLog>(
      "GET",
      `/v1/memories/${encodeURIComponent(memoryId)}/audit`,
    );
  }
}
