/**
 * Official TypeScript SDK for the SCP Memory Engine (Phase 5).
 *
 * Covers the full v1 surface: memory CRUD + audit, intelligence (decay/dedup/
 * consolidate), hybrid retrieval, and the trust layer.
 */

export { SCPMemoryClient } from "./client.js";
export { ApiError, NotFoundError, ValidationError } from "./errors.js";
export { HttpClient } from "./http.js";
export type { HttpClientOptions, FetchFn } from "./http.js";
export type * from "./types.js";
