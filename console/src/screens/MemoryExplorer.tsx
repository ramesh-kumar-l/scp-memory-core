/* Memory Explorer — browse/filter/inspect memories in the active namespace, with
   create + delete and a detail/audit panel. Namespace comes from global Settings. */

import { useState } from "react";
import type { MemoryType } from "@scp/memory-sdk";
import { PageHead } from "../components/PageHead";
import { StateBadge } from "../components/Badge";
import { EmptyState, ErrorState, Loading } from "../components/States";
import { MemoryDetail } from "./MemoryDetail";
import { useMemories } from "../api/queries";
import { useCreateMemory, useDeleteMemory, useIntelligencePass } from "../api/mutations";
import { useSettings } from "../state/settings";

const TYPES: MemoryType[] = ["fact", "event", "preference", "summary", "other"];
const STATES = ["active", "archived", "decayed", "superseded"];
const PAGE = 25;

export function MemoryExplorer() {
  const { settings } = useSettings();
  const ns = settings.namespace;
  const [type, setType] = useState<MemoryType | "">("");
  const [state, setState] = useState("");
  const [offset, setOffset] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const list = useMemories({
    namespace: ns,
    type: type || undefined,
    state: state || undefined,
    limit: PAGE,
    offset,
  });
  const del = useDeleteMemory(ns);
  const pass = useIntelligencePass();

  const onDelete = (id: string) =>
    del.mutate(id, { onSuccess: () => selected === id && setSelected(null) });

  return (
    <>
      <PageHead
        title="Memory Explorer"
        subtitle={`Namespace ${ns}`}
        actions={
          <>
            <button className="btn" onClick={() => pass.mutate({ pass: "dedup", namespace: ns })} disabled={pass.isPending}>
              Dedup
            </button>
            <button className="btn" onClick={() => pass.mutate({ pass: "decay", namespace: ns })} disabled={pass.isPending}>
              Decay
            </button>
            <button className="btn btn--primary" onClick={() => setCreating((v) => !v)}>
              {creating ? "Close" : "New memory"}
            </button>
          </>
        }
      />

      {creating && <CreateForm namespace={ns} onDone={() => setCreating(false)} />}

      <div className="toolbar" style={{ marginBottom: "var(--space-3)" }}>
        <Filter label="Type" value={type} onChange={(v) => setType(v as MemoryType | "")} options={TYPES} />
        <Filter label="State" value={state} onChange={setState} options={STATES} />
      </div>

      <div className="split">
        <div className="card">
          {list.isLoading ? (
            <div className="card--pad">
              <Loading label="Loading memories" />
            </div>
          ) : list.isError ? (
            <ErrorState error={list.error} onRetry={() => list.refetch()} />
          ) : list.data!.items.length === 0 ? (
            <EmptyState title="No memories here yet" hint="Create one, or adjust the filters." />
          ) : (
            <>
              <table className="table">
                <thead>
                  <tr>
                    <th>Content</th>
                    <th>Type</th>
                    <th>State</th>
                  </tr>
                </thead>
                <tbody>
                  {list.data!.items.map((m) => (
                    <tr
                      key={m.id}
                      aria-selected={selected === m.id}
                      onClick={() => setSelected(m.id)}
                    >
                      <td>{truncate(m.content)}</td>
                      <td>{m.type}</td>
                      <td>
                        <StateBadge state={m.state} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <Pager
                total={list.data!.total}
                offset={offset}
                onPrev={() => setOffset(Math.max(0, offset - PAGE))}
                onNext={() => setOffset(offset + PAGE)}
              />
            </>
          )}
        </div>

        {selected ? (
          <MemoryDetail
            memoryId={selected}
            namespace={ns}
            onDelete={() => onDelete(selected)}
            deleting={del.isPending}
          />
        ) : (
          <div className="card card--pad">
            <EmptyState title="Select a memory" hint="Pick a row to inspect fields and its audit trail." />
          </div>
        )}
      </div>
    </>
  );
}

function Filter({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: string[];
}) {
  return (
    <label className="field">
      <span className="field__label">{label}</span>
      <select className="select" value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="">All</option>
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </label>
  );
}

function Pager({
  total,
  offset,
  onPrev,
  onNext,
}: {
  total: number;
  offset: number;
  onPrev: () => void;
  onNext: () => void;
}) {
  const start = total === 0 ? 0 : offset + 1;
  const end = Math.min(offset + PAGE, total);
  return (
    <div className="row card--pad" style={{ borderTop: "1px solid var(--border)" }}>
      <span className="stat__label">
        {start}–{end} of {total}
      </span>
      <div className="row pull-right">
        <button className="btn" onClick={onPrev} disabled={offset === 0}>
          Prev
        </button>
        <button className="btn" onClick={onNext} disabled={end >= total}>
          Next
        </button>
      </div>
    </div>
  );
}

function CreateForm({ namespace, onDone }: { namespace: string; onDone: () => void }) {
  const create = useCreateMemory();
  const [content, setContent] = useState("");
  const [type, setType] = useState<MemoryType>("fact");
  const [source, setSource] = useState("");

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;
    create.mutate(
      { content: content.trim(), namespace, type, source: source.trim() || undefined },
      { onSuccess: onDone },
    );
  };

  return (
    <form className="card card--pad stack" style={{ marginBottom: "var(--space-3)" }} onSubmit={submit}>
      <label className="field">
        <span className="field__label">Content</span>
        <textarea className="textarea" value={content} onChange={(e) => setContent(e.target.value)} />
      </label>
      <div className="toolbar">
        <label className="field">
          <span className="field__label">Type</span>
          <select className="select" value={type} onChange={(e) => setType(e.target.value as MemoryType)}>
            {TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span className="field__label">Source</span>
          <input className="input" value={source} onChange={(e) => setSource(e.target.value)} />
        </label>
        <button className="btn btn--primary" type="submit" disabled={create.isPending || !content.trim()}>
          {create.isPending ? "Saving…" : "Save"}
        </button>
      </div>
      {create.isError && <span style={{ color: "var(--danger)" }}>Could not create memory.</span>}
    </form>
  );
}

function truncate(s: string, n = 80): string {
  return s.length > n ? `${s.slice(0, n)}…` : s;
}
