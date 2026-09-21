/** Response & request types mirroring the API schemas (src/scp_memory/schemas). */

export type MemoryType = "fact" | "event" | "preference" | "summary" | "other";
export type RetrievalMode = "keyword" | "vector" | "hybrid";

export interface Memory {
  id: string;
  content: string;
  type: string;
  state: string;
  namespace: string;
  importance: number | null;
  access_count: number;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  last_accessed_at: string | null;
}

export interface MemoryPage {
  items: Memory[];
  total: number;
  limit: number;
  offset: number;
}

export interface AuditEvent {
  id: string;
  memory_id: string;
  action: string;
  actor: string;
  timestamp: string;
  diff: Record<string, unknown>;
}

export interface AuditLog {
  items: AuditEvent[];
  total: number;
}

export interface TrustBreakdown {
  provenance_quality: number;
  confidence: number;
  freshness: number;
  score: number;
  explanation: string;
}

export interface SignalScores {
  keyword: number;
  vector: number;
  metadata: number;
  importance: number;
  trust: number;
}

export interface SearchResult {
  memory: Memory;
  score: number;
  signals: SignalScores;
  weights: Record<string, number>;
  trust: TrustBreakdown;
}

export interface SearchResponse {
  query: string;
  namespace: string;
  mode: string;
  count: number;
  results: SearchResult[];
}

export interface DecayResult {
  namespace: string;
  scanned: number;
  decayed: string[];
}

export interface DedupCluster {
  canonical: string;
  merged: string[];
}

export interface DedupResult {
  namespace: string;
  clusters: DedupCluster[];
  merged_count: number;
}

export interface ConsolidateResult {
  summary: Memory;
  source_ids: string[];
}

export interface CreateMemoryParams {
  content: string;
  namespace: string;
  type?: MemoryType;
  metadata?: Record<string, unknown>;
  source?: string;
}

export interface UpdateMemoryParams {
  content?: string;
  type?: MemoryType;
  metadata?: Record<string, unknown>;
  namespace?: string;
}

export interface ListMemoriesParams {
  namespace: string;
  type?: MemoryType;
  state?: string;
  limit?: number;
  offset?: number;
}

export interface SearchParams {
  query: string;
  namespace: string;
  k?: number;
  mode?: RetrievalMode;
  type?: MemoryType;
  state?: string;
  minConfidence?: number;
}
