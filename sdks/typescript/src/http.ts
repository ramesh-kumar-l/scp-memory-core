/**
 * Thin transport over the Fetch API (Node 18+, browsers, Deno).
 *
 * Owns the base URL, the `X-Actor` audit header, query-param cleanup, and
 * mapping of the server error envelope to typed exceptions. A custom `fetchFn`
 * can be injected for tests or non-global-fetch runtimes.
 */

import { ApiError, NotFoundError, ValidationError } from "./errors.js";

export type FetchFn = typeof fetch;

export interface HttpClientOptions {
  baseUrl: string;
  actor?: string;
  fetchFn?: FetchFn;
}

export type QueryValue = string | number | boolean | undefined | null;

interface RequestOptions {
  params?: Record<string, QueryValue>;
  body?: unknown;
}

export class HttpClient {
  private readonly baseUrl: string;
  private readonly actor: string | undefined;
  private readonly fetchFn: FetchFn;

  constructor(options: HttpClientOptions) {
    this.baseUrl = options.baseUrl.replace(/\/+$/, "");
    this.actor = options.actor;
    this.fetchFn = options.fetchFn ?? fetch;
  }

  async request<T>(method: string, path: string, options: RequestOptions = {}): Promise<T> {
    const url = new URL(this.baseUrl + path);
    for (const [key, value] of Object.entries(options.params ?? {})) {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, String(value));
      }
    }

    const headers: Record<string, string> = {};
    if (options.body !== undefined) {
      headers["content-type"] = "application/json";
    }
    if (this.actor) {
      headers["x-actor"] = this.actor;
    }

    const response = await this.fetchFn(url.toString(), {
      method,
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    });

    if (!response.ok) {
      await raise(response);
    }
    if (response.status === 204) {
      return undefined as T;
    }
    const text = await response.text();
    return (text ? JSON.parse(text) : undefined) as T;
  }
}

async function raise(response: Response): Promise<never> {
  let code = "error";
  let message = response.statusText;
  let details: Record<string, unknown> | undefined;
  try {
    const body = (await response.json()) as { error?: Record<string, unknown> };
    const err = body.error ?? {};
    code = (err.code as string) ?? code;
    message = (err.message as string) ?? message;
    details = err.details as Record<string, unknown> | undefined;
  } catch {
    // non-JSON error body; keep status text
  }
  const status = response.status;
  if (status === 404) throw new NotFoundError(status, code, message, details);
  if (status === 400 || status === 422) throw new ValidationError(status, code, message, details);
  throw new ApiError(status, code, message, details);
}
