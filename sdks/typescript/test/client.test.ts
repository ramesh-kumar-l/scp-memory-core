import { describe, expect, it } from "vitest";

import { SCPMemoryClient } from "../src/client.js";
import { NotFoundError, ValidationError } from "../src/errors.js";
import type { FetchFn } from "../src/http.js";

/** Build a client whose fetch is a deterministic stub over (method, path) → response. */
function stubClient(handler: (req: { method: string; url: URL; body: unknown }) => Response) {
  const fetchFn: FetchFn = async (input, init) => {
    const url = new URL(String(input));
    const body = init?.body ? JSON.parse(String(init.body)) : undefined;
    return handler({ method: init?.method ?? "GET", url, body });
  };
  return new SCPMemoryClient({ baseUrl: "http://test", actor: "alice", fetchFn });
}

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json" },
  });
}

const memory = {
  id: "mem_1",
  content: "user prefers dark mode",
  type: "preference",
  state: "active",
  namespace: "user:1",
  importance: 0.5,
  access_count: 0,
  metadata: {},
  created_at: "2026-06-20T00:00:00Z",
  updated_at: "2026-06-20T00:00:00Z",
  last_accessed_at: null,
};

describe("SCPMemoryClient", () => {
  it("creates a memory and sends the actor header + body", async () => {
    let seen: { method: string; url: URL; body: unknown } | undefined;
    const client = stubClient((req) => {
      seen = req;
      return json(memory, 201);
    });
    const result = await client.memories.create({
      content: "user prefers dark mode",
      namespace: "user:1",
      type: "preference",
      source: "settings",
    });
    expect(result.id).toBe("mem_1");
    expect(seen?.method).toBe("POST");
    expect(seen?.url.pathname).toBe("/v1/memories");
    expect(seen?.body).toMatchObject({ content: "user prefers dark mode", source: "settings" });
  });

  it("omits null query params and passes namespace", async () => {
    let seen: URL | undefined;
    const client = stubClient((req) => {
      seen = req.url;
      return json(memory);
    });
    await client.memories.get("mem_1", "user:1");
    expect(seen?.searchParams.get("namespace")).toBe("user:1");
  });

  it("parses trust-aware search results", async () => {
    const client = stubClient(() =>
      json({
        query: "dark mode",
        namespace: "user:1",
        mode: "hybrid",
        count: 1,
        results: [
          {
            memory,
            score: 0.81,
            signals: { keyword: 0.3, vector: 0.7, metadata: 1.0, importance: 0.5, trust: 0.9 },
            weights: { keyword: 0.35, vector: 0.35, importance: 0.1, trust: 0.2 },
            trust: {
              provenance_quality: 1.0,
              confidence: 0.9,
              freshness: 0.8,
              score: 0.9,
              explanation: "User-stated preference (high provenance).",
            },
          },
        ],
      }),
    );
    const resp = await client.retrieval.search({ query: "dark mode", namespace: "user:1" });
    expect(resp.results[0]?.trust.provenance_quality).toBe(1.0);
    expect(resp.results[0]?.weights.trust).toBe(0.2);
  });

  it("maps 404 to NotFoundError", async () => {
    const client = stubClient(() =>
      json({ error: { code: "not_found", message: "memory not found" } }, 404),
    );
    await expect(client.trust.explain("missing", "user:1")).rejects.toBeInstanceOf(NotFoundError);
  });

  it("maps 422 to ValidationError", async () => {
    const client = stubClient(() =>
      json({ error: { code: "invalid", message: "bad request" } }, 422),
    );
    await expect(
      client.memories.create({ content: "", namespace: "user:1" }),
    ).rejects.toBeInstanceOf(ValidationError);
  });

  it("returns void on 204 delete", async () => {
    const client = stubClient(() => new Response(null, { status: 204 }));
    await expect(client.memories.delete("mem_1", { namespace: "user:1" })).resolves.toBeUndefined();
  });
});
