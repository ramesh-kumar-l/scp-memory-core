/* Global console settings: the active namespace, engine base URL, audit actor,
   and theme. Persisted to localStorage so a reload keeps context. These are the
   inputs every screen shares (Settings screen edits them). */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

export type Theme = "light" | "dark";

export interface ConsoleSettings {
  baseUrl: string;
  namespace: string;
  actor: string;
  theme: Theme;
}

const STORAGE_KEY = "scp-console-settings";

const DEFAULTS: ConsoleSettings = {
  baseUrl: typeof window !== "undefined" ? window.location.origin : "http://localhost:8000",
  namespace: "user:demo",
  actor: "console",
  theme: "light",
};

function load(): ConsoleSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return { ...DEFAULTS, ...(JSON.parse(raw) as Partial<ConsoleSettings>) };
  } catch {
    /* ignore corrupt storage */
  }
  return DEFAULTS;
}

interface SettingsContextValue {
  settings: ConsoleSettings;
  update: (patch: Partial<ConsoleSettings>) => void;
  toggleTheme: () => void;
}

const SettingsContext = createContext<SettingsContextValue | null>(null);

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<ConsoleSettings>(load);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    document.documentElement.dataset.theme = settings.theme;
  }, [settings]);

  const update = useCallback(
    (patch: Partial<ConsoleSettings>) => setSettings((prev) => ({ ...prev, ...patch })),
    [],
  );
  const toggleTheme = useCallback(
    () => setSettings((prev) => ({ ...prev, theme: prev.theme === "light" ? "dark" : "light" })),
    [],
  );

  const value = useMemo(() => ({ settings, update, toggleTheme }), [settings, update, toggleTheme]);
  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
}

export function useSettings(): SettingsContextValue {
  const ctx = useContext(SettingsContext);
  if (!ctx) throw new Error("useSettings must be used within <SettingsProvider>");
  return ctx;
}
