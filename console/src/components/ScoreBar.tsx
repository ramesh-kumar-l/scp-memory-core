/* A labelled 0..1 bar — the core "explainability made visual" primitive used by
   the Retrieval Inspector (per-signal scores) and Trust Explorer (dimensions). */

export function ScoreBar({ label, value }: { label: string; value: number }) {
  const pct = Math.max(0, Math.min(1, value)) * 100;
  return (
    <div className="scorebar">
      <span>{label}</span>
      <span className="scorebar__track" role="meter" aria-valuenow={Number(value.toFixed(2))} aria-valuemin={0} aria-valuemax={1} aria-label={label}>
        <span className="scorebar__fill" style={{ width: `${pct}%` }} />
      </span>
      <span className="scorebar__val">{value.toFixed(2)}</span>
    </div>
  );
}
