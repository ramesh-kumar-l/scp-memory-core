/* Retrieval Inspector — run a hybrid query and see, per candidate, the fused
   score broken into its signals (keyword/vector/metadata/importance/trust) and
   the weights applied. This is the explainability surface for retrieval. */

import { useState } from "react";
import type { RetrievalMode, SearchParams, SearchResult } from "@scp/memory-sdk";
import { PageHead } from "../components/PageHead";
import { ScoreBadge, StateBadge } from "../components/Badge";
import { ScoreBar } from "../components/ScoreBar";
import { EmptyState, ErrorState, Loading } from "../components/States";
import { useSearch } from "../api/queries";
import { useSettings } from "../state/settings";

const MODES: RetrievalMode[] = ["hybrid", "keyword", "vector"];
const SIGNALS: Array<keyof SearchResult["signals"]> = [
  "keyword",
  "vector",
  "metadata",
  "importance",
  "trust",
];

export function RetrievalInspector() {
  const { settings } = useSettings();
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<RetrievalMode>("hybrid");
  const [k, setK] = useState(10);
  const [minConfidence, setMinConfidence] = useState(0);
  const [submitted, setSubmitted] = useState<SearchParams | null>(null);

  const search = useSearch(submitted);

  const run = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setSubmitted({
      query: query.trim(),
      namespace: settings.namespace,
      mode,
      k,
      minConfidence: minConfidence || undefined,
    });
  };

  return (
    <>
      <PageHead title="Retrieval Inspector" subtitle={`Namespace ${settings.namespace}`} />

      <form className="card card--pad stack" style={{ marginBottom: "var(--space-4)" }} onSubmit={run}>
        <label className="field">
          <span className="field__label">Query</span>
          <input
            className="input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. what theme does the user prefer?"
            autoFocus
          />
        </label>
        <div className="toolbar">
          <label className="field">
            <span className="field__label">Mode</span>
            <select className="select" value={mode} onChange={(e) => setMode(e.target.value as RetrievalMode)}>
              {MODES.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span className="field__label">k</span>
            <input
              className="input"
              type="number"
              min={1}
              max={50}
              value={k}
              onChange={(e) => setK(Number(e.target.value))}
            />
          </label>
          <label className="field">
            <span className="field__label">Min confidence</span>
            <input
              className="input"
              type="number"
              min={0}
              max={1}
              step={0.05}
              value={minConfidence}
              onChange={(e) => setMinConfidence(Number(e.target.value))}
            />
          </label>
          <button className="btn btn--primary" type="submit" disabled={!query.trim()}>
            Search
          </button>
        </div>
      </form>

      {!submitted ? (
        <EmptyState title="Run a query" hint="Results show each candidate's per-signal scores." />
      ) : search.isLoading ? (
        <Loading label="Searching" />
      ) : search.isError ? (
        <ErrorState error={search.error} onRetry={() => search.refetch()} />
      ) : search.data!.results.length === 0 ? (
        <EmptyState title="No matches" hint="Try a broader query or a different mode." />
      ) : (
        <div className="stack">
          <span className="stat__label">
            {search.data!.count} result(s) · mode {search.data!.mode}
          </span>
          {search.data!.results.map((r) => (
            <ResultCard key={r.memory.id} result={r} />
          ))}
        </div>
      )}
    </>
  );
}

function ResultCard({ result }: { result: SearchResult }) {
  const { memory, score, signals, weights, trust } = result;
  return (
    <div className="card card--pad stack">
      <div className="row">
        <strong>score {score.toFixed(3)}</strong>
        <StateBadge state={memory.state} />
        <span className="badge badge--neutral">{memory.type}</span>
        <span className="pull-right">
          <ScoreBadge value={trust.confidence} label="conf" />
        </span>
      </div>
      <p style={{ margin: 0 }}>{memory.content}</p>
      <div className="split">
        <div className="stack" style={{ gap: "var(--space-1)" }}>
          {SIGNALS.map((s) => (
            <ScoreBar key={s} label={`${s} ×${(weights[s] ?? 0).toFixed(2)}`} value={signals[s]} />
          ))}
        </div>
        <dl className="kv">
          <dt>Provenance</dt>
          <dd>{trust.provenance_quality.toFixed(2)}</dd>
          <dt>Freshness</dt>
          <dd>{trust.freshness.toFixed(2)}</dd>
          <dt>Trust score</dt>
          <dd>{trust.score.toFixed(2)}</dd>
          <dt>ID</dt>
          <dd className="mono">{memory.id}</dd>
        </dl>
      </div>
      <p className="stat__label" style={{ margin: 0 }}>
        {trust.explanation}
      </p>
    </div>
  );
}
