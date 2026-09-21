/* Semantic badges for memory state and a 0..1 trust/confidence score. Color is
   meaning, not decoration (19-ui-design-system: semantic colors for state/trust). */

type Tone = "ok" | "warn" | "danger" | "info" | "neutral";

export function Badge({ tone = "neutral", children }: { tone?: Tone; children: React.ReactNode }) {
  return <span className={`badge badge--${tone}`}>{children}</span>;
}

const STATE_TONE: Record<string, Tone> = {
  active: "ok",
  archived: "neutral",
  decayed: "warn",
  deleted: "danger",
  superseded: "info",
};

export function StateBadge({ state }: { state: string }) {
  return <Badge tone={STATE_TONE[state] ?? "neutral"}>{state}</Badge>;
}

/** 0..1 score → tone band. Used for confidence/trust/freshness chips. */
export function ScoreBadge({ value, label }: { value: number; label?: string }) {
  const tone: Tone = value >= 0.66 ? "ok" : value >= 0.33 ? "warn" : "danger";
  return (
    <Badge tone={tone}>
      {label ? `${label} ` : ""}
      {value.toFixed(2)}
    </Badge>
  );
}
