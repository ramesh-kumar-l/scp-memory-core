/* Builds the official SDK client from the current console settings, and a thin
   fetch helper for the ops endpoints the SDK does not cover (readiness, metrics). */

import { SCPMemoryClient } from "@scp/memory-sdk";
import type { ConsoleSettings } from "../state/settings";

export function makeClient(settings: ConsoleSettings): SCPMemoryClient {
  return new SCPMemoryClient({ baseUrl: settings.baseUrl, actor: settings.actor });
}

export interface ReadyStatus {
  status: string;
  database?: string;
  ok: boolean;
}

/** Readiness probe (GET /health/ready) — 503 maps to ok:false, not a throw. */
export async function fetchReady(baseUrl: string): Promise<ReadyStatus> {
  const res = await fetch(`${baseUrl}/health/ready`);
  const body = (await res.json().catch(() => ({}))) as { status?: string; database?: string };
  return { status: body.status ?? "unknown", database: body.database, ok: res.ok };
}

/** Raw Prometheus exposition text (GET /metrics). */
export async function fetchMetricsText(baseUrl: string): Promise<string> {
  const res = await fetch(`${baseUrl}/metrics`);
  if (!res.ok) throw new Error(`metrics endpoint returned ${res.status}`);
  return res.text();
}
