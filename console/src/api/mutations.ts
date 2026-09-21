/* Write-path hooks (create/delete memory, intelligence passes). Each invalidates
   the read caches it affects so the UI reflects the new state without a reload. */

import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { CreateMemoryParams, DecayResult, DedupResult } from "@scp/memory-sdk";
import { useClient } from "./queries";

export function useCreateMemory() {
  const client = useClient();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (params: CreateMemoryParams) => client.memories.create(params),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["memories"] }),
  });
}

export function useDeleteMemory(namespace: string) {
  const client = useClient();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (memoryId: string) => client.memories.delete(memoryId, { namespace }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["memories"] }),
  });
}

export type IntelligencePass = "decay" | "dedup";

export function useIntelligencePass() {
  const client = useClient();
  const qc = useQueryClient();
  return useMutation<DecayResult | DedupResult, Error, { pass: IntelligencePass; namespace: string }>({
    mutationFn: ({ pass, namespace }) =>
      pass === "decay" ? client.intelligence.decay(namespace) : client.intelligence.dedup(namespace),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["memories"] }),
  });
}
