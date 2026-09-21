/* Trust Explorer — for a given memory, visualise the trust dimensions
   (provenance quality, confidence, freshness) that compose its score, plus the
   human-readable explanation the engine emits. */

import { useState } from "react";
import { PageHead } from "../components/PageHead";
import { ScoreBadge } from "../components/Badge";
import { ScoreBar } from "../components/ScoreBar";
import { EmptyState, ErrorState, Loading } from "../components/States";
import { useTrust } from "../api/queries";
import { useSettings } from "../state/settings";

export function TrustExplorer() {
  const { settings } = useSettings();
  const [idInput, setIdInput] = useState("");
  const [memoryId, setMemoryId] = useState<string | null>(null);
  const trust = useTrust(memoryId, settings.namespace);

  const run = (e: React.FormEvent) => {
    e.preventDefault();
    setMemoryId(idInput.trim() || null);
  };

  return (
    <>
      <PageHead title="Trust Explorer" subtitle={`Namespace ${settings.namespace}`} />

      <form className="card card--pad toolbar" style={{ marginBottom: "var(--space-4)" }} onSubmit={run}>
        <label className="field" style={{ flex: 1, minWidth: 280 }}>
          <span className="field__label">Memory ID</span>
          <input
            className="input mono"
            value={idInput}
            onChange={(e) => setIdInput(e.target.value)}
            placeholder="mem_…  (copy from Memory Explorer or Retrieval)"
          />
        </label>
        <button className="btn btn--primary" type="submit" disabled={!idInput.trim()}>
          Explain
        </button>
      </form>

      {!memoryId ? (
        <EmptyState
          title="Inspect a memory's trust"
          hint="Paste a memory ID to see why it is (or isn't) trustworthy."
        />
      ) : trust.isLoading ? (
        <Loading rows={3} label="Evaluating trust" />
      ) : trust.isError ? (
        <ErrorState error={trust.error} onRetry={() => trust.refetch()} />
      ) : (
        <div className="card card--pad stack" style={{ maxWidth: 640 }}>
          <div className="row">
            <strong>Trust score</strong>
            <span className="pull-right">
              <ScoreBadge value={trust.data!.score} />
            </span>
          </div>
          <div className="stack" style={{ gap: "var(--space-1)" }}>
            <ScoreBar label="Provenance" value={trust.data!.provenance_quality} />
            <ScoreBar label="Confidence" value={trust.data!.confidence} />
            <ScoreBar label="Freshness" value={trust.data!.freshness} />
          </div>
          <p className="stat__label" style={{ margin: 0 }}>
            {trust.data!.explanation}
          </p>
        </div>
      )}
    </>
  );
}
