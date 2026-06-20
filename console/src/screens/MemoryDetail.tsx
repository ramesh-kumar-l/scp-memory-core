/* Right-hand inspector for a selected memory: full fields, metadata, and the
   append-only audit trail (provenance of every mutation). */

import { StateBadge } from "../components/Badge";
import { ErrorState, Loading } from "../components/States";
import { useAudit, useMemory } from "../api/queries";

export function MemoryDetail({
  memoryId,
  namespace,
  onDelete,
  deleting,
}: {
  memoryId: string;
  namespace: string;
  onDelete: () => void;
  deleting: boolean;
}) {
  const memory = useMemory(memoryId, namespace);
  const audit = useAudit(memoryId);

  if (memory.isLoading) return <Loading rows={4} label="Loading memory" />;
  if (memory.isError) return <ErrorState error={memory.error} onRetry={() => memory.refetch()} />;
  const m = memory.data!;

  return (
    <div className="stack">
      <div className="card card--pad stack">
        <div className="row">
          <StateBadge state={m.state} />
          <span className="badge badge--neutral">{m.type}</span>
          <button className="btn pull-right" onClick={onDelete} disabled={deleting}>
            {deleting ? "Deleting…" : "Delete"}
          </button>
        </div>
        <p style={{ margin: 0 }}>{m.content}</p>
        <dl className="kv">
          <dt>ID</dt>
          <dd className="mono">{m.id}</dd>
          <dt>Namespace</dt>
          <dd className="mono">{m.namespace}</dd>
          <dt>Importance</dt>
          <dd>{m.importance == null ? "—" : m.importance.toFixed(3)}</dd>
          <dt>Access count</dt>
          <dd>{m.access_count}</dd>
          <dt>Created</dt>
          <dd>{fmtTime(m.created_at)}</dd>
          <dt>Updated</dt>
          <dd>{fmtTime(m.updated_at)}</dd>
          {Object.keys(m.metadata ?? {}).length > 0 && (
            <>
              <dt>Metadata</dt>
              <dd className="mono">{JSON.stringify(m.metadata)}</dd>
            </>
          )}
        </dl>
      </div>

      <div className="card card--pad stack">
        <strong>Audit trail</strong>
        {audit.isLoading ? (
          <Loading rows={3} label="Loading audit" />
        ) : audit.isError ? (
          <ErrorState error={audit.error} onRetry={() => audit.refetch()} />
        ) : (audit.data?.items.length ?? 0) === 0 ? (
          <span className="stat__label">No audit events.</span>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Action</th>
                <th>Actor</th>
                <th>When</th>
              </tr>
            </thead>
            <tbody>
              {audit.data!.items.map((e) => (
                <tr key={e.id} style={{ cursor: "default" }}>
                  <td>{e.action}</td>
                  <td>{e.actor}</td>
                  <td>{fmtTime(e.timestamp)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function fmtTime(iso: string): string {
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString();
}
