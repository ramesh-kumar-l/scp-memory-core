/* React Query hooks over the SDK + ops endpoints. Centralising fetch/cache here
   keeps screens declarative and gives every screen consistent loading/error
   states (19-ui-design-system required states). */

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import type {
  AuditLog,
  ListMemoriesParams,
  Memory,
  MemoryPage,
  SearchParams,
  SearchResponse,
  TrustBreakdown,
} from "@scp/memory-sdk";
import { fetchMetricsText, fetchReady, makeClient } from "./client";
import { parseMetrics, type Sample } from "./metrics";
import { useSettings } from "../state/settings";

export function useClient() {
  const { settings } = useSettings();
  return useMemo(() => makeClient(settings), [settings]);
}

export function useMemories(params: ListMemoriesParams) {
  const client = useClient();
  return useQuery<MemoryPage>({
    queryKey: ["memories", params],
    queryFn: () => client.memories.list(params),
  });
}

export function useMemory(memoryId: string | null, namespace: string) {
  const client = useClient();
  return useQuery<Memory>({
    queryKey: ["memory", memoryId, namespace],
    queryFn: () => client.memories.get(memoryId as string, namespace),
    enabled: Boolean(memoryId),
  });
}

export function useAudit(memoryId: string | null) {
  const client = useClient();
  return useQuery<AuditLog>({
    queryKey: ["audit", memoryId],
    queryFn: () => client.memories.audit(memoryId as string),
    enabled: Boolean(memoryId),
  });
}

export function useSearch(params: SearchParams | null) {
  const client = useClient();
  return useQuery<SearchResponse>({
    queryKey: ["search", params],
    queryFn: () => client.retrieval.search(params as SearchParams),
    enabled: Boolean(params),
  });
}

export function useTrust(memoryId: string | null, namespace: string) {
  const client = useClient();
  return useQuery<TrustBreakdown>({
    queryKey: ["trust", memoryId, namespace],
    queryFn: () => client.trust.explain(memoryId as string, namespace),
    enabled: Boolean(memoryId),
  });
}

export function useReady() {
  const { settings } = useSettings();
  return useQuery({
    queryKey: ["ready", settings.baseUrl],
    queryFn: () => fetchReady(settings.baseUrl),
    refetchInterval: 15_000,
  });
}

export function useMetrics() {
  const { settings } = useSettings();
  return useQuery<Sample[]>({
    queryKey: ["metrics", settings.baseUrl],
    queryFn: async () => parseMetrics(await fetchMetricsText(settings.baseUrl)),
    refetchInterval: 15_000,
  });
}
