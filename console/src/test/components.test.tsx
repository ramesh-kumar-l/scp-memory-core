import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { ScoreBadge, StateBadge } from "../components/Badge";
import { ScoreBar } from "../components/ScoreBar";
import { EmptyState, ErrorState } from "../components/States";

describe("UI primitives", () => {
  it("renders an empty state as a status", () => {
    render(<EmptyState title="Nothing here" hint="Add one" />);
    expect(screen.getByRole("status")).toHaveTextContent("Nothing here");
  });

  it("maps a network error to a friendly, actionable message", () => {
    render(<ErrorState error={new Error("Failed to fetch")} />);
    expect(screen.getByRole("alert")).toHaveTextContent(/could not reach the engine/i);
  });

  it("colours a state badge by meaning", () => {
    const { container } = render(<StateBadge state="decayed" />);
    expect(container.querySelector(".badge--warn")).not.toBeNull();
  });

  it("bands a score badge and exposes a meter on the bar", () => {
    const { container } = render(<ScoreBadge value={0.9} />);
    expect(container.querySelector(".badge--ok")).not.toBeNull();
    render(<ScoreBar label="vector" value={0.5} />);
    expect(screen.getByRole("meter", { name: "vector" })).toHaveAttribute("aria-valuenow", "0.5");
  });
});
