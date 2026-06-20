/* App shell: persistent sidebar + routed main pane. Routes map 1:1 to the six
   Phase-7 screens (19-ui-design-system). */

import { Route, Routes } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";
import { Dashboard } from "./screens/Dashboard";
import { MemoryExplorer } from "./screens/MemoryExplorer";
import { RetrievalInspector } from "./screens/RetrievalInspector";
import { TrustExplorer } from "./screens/TrustExplorer";
import { Benchmarks } from "./screens/Benchmarks";
import { Settings } from "./screens/Settings";

export function App() {
  return (
    <div className="shell">
      <Sidebar />
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/memories" element={<MemoryExplorer />} />
          <Route path="/retrieval" element={<RetrievalInspector />} />
          <Route path="/trust" element={<TrustExplorer />} />
          <Route path="/benchmarks" element={<Benchmarks />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  );
}
