/* Settings — the shared context every screen reads: active namespace, engine
   base URL, audit actor, and theme. Edits persist to localStorage immediately. */

import { PageHead } from "../components/PageHead";
import { useReady } from "../api/queries";
import { useSettings } from "../state/settings";

export function Settings() {
  const { settings, update, toggleTheme } = useSettings();
  const ready = useReady();

  return (
    <>
      <PageHead title="Settings" subtitle="Connection, namespace, and appearance" />

      <div className="card card--pad stack" style={{ maxWidth: 560 }}>
        <label className="field">
          <span className="field__label">Active namespace</span>
          <input
            className="input"
            value={settings.namespace}
            onChange={(e) => update({ namespace: e.target.value })}
          />
        </label>

        <label className="field">
          <span className="field__label">Engine base URL</span>
          <input
            className="input mono"
            value={settings.baseUrl}
            onChange={(e) => update({ baseUrl: e.target.value })}
          />
          <span className="stat__label">
            Same-origin by default; in dev the bundler proxies /v1, /health and /metrics
            to the engine.
          </span>
        </label>

        <label className="field">
          <span className="field__label">Audit actor</span>
          <input
            className="input"
            value={settings.actor}
            onChange={(e) => update({ actor: e.target.value })}
          />
          <span className="stat__label">Sent as the X-Actor header on every mutating call.</span>
        </label>

        <div className="field">
          <span className="field__label">Theme</span>
          <div className="row">
            <button className="btn" onClick={toggleTheme}>
              Switch to {settings.theme === "light" ? "dark" : "light"}
            </button>
            <span className="stat__label">Current: {settings.theme}</span>
          </div>
        </div>

        <div className="field">
          <span className="field__label">Engine readiness</span>
          <span className="stat__label">
            {ready.isLoading
              ? "checking…"
              : ready.data?.ok
                ? `ready (database: ${ready.data.database ?? "ok"})`
                : "not ready / unreachable"}
          </span>
        </div>
      </div>
    </>
  );
}
