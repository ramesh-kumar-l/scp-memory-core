/* Left navigation. Keyboard-operable (native links + NavLink focus rings) and
   marks the active route via aria-current for both styling and screen readers. */

import { NavLink } from "react-router-dom";

const LINKS = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/memories", label: "Memory Explorer", end: false },
  { to: "/retrieval", label: "Retrieval Inspector", end: false },
  { to: "/trust", label: "Trust Explorer", end: false },
  { to: "/benchmarks", label: "Benchmarks", end: false },
  { to: "/settings", label: "Settings", end: false },
];

export function Sidebar() {
  return (
    <nav className="sidebar" aria-label="Primary">
      <div className="sidebar__brand">SCP Memory</div>
      {LINKS.map((link) => (
        <NavLink key={link.to} to={link.to} end={link.end} className="nav-link">
          {link.label}
        </NavLink>
      ))}
    </nav>
  );
}
