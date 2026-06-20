/* The three required states for every screen (19-ui-design-system): Empty,
   Loading (skeletons, no layout shift), and Error (actionable, non-technical). */

import type { ReactNode } from "react";

export function EmptyState({ title, hint }: { title: string; hint?: ReactNode }) {
  return (
    <div className="state" role="status">
      <div className="state__title">{title}</div>
      {hint && <div>{hint}</div>}
    </div>
  );
}

export function Loading({ rows = 5, label = "Loading" }: { rows?: number; label?: string }) {
  return (
    <div className="stack" role="status" aria-busy="true" aria-label={label}>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="skeleton" style={{ height: 40 }} />
      ))}
    </div>
  );
}

export function ErrorState({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  const message = friendly(error);
  return (
    <div className="state" role="alert">
      <div className="state__title">Something went wrong</div>
      <div>{message}</div>
      {onRetry && (
        <button className="btn" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}

function friendly(error: unknown): string {
  const raw = error instanceof Error ? error.message : String(error);
  if (/failed to fetch|networkerror/i.test(raw)) {
    return "Could not reach the engine. Check that it is running and the base URL in Settings is correct.";
  }
  if (/404|not\s*found/i.test(raw)) return "That item could not be found in this namespace.";
  return raw || "Unexpected error.";
}
