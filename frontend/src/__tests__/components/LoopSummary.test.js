import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import LoopSummary from "../../components/LoopSummary";

const baseProgress = {
  answered: 10,
  correct: 7,
  incorrect: 3,
  loopNumber: 1,
  total: 10,
  loopComplete: true,
};

describe("LoopSummary", () => {
  it("renders loop number and total", () => {
    render(<LoopSummary loopProgress={baseProgress} onNextLoop={jest.fn()} />);

    expect(screen.getByText("Loop 1 Complete")).toBeInTheDocument();
    expect(screen.getByText("You answered all 10 questions")).toBeInTheDocument();
  });

  it("shows correct and incorrect counts", () => {
    render(<LoopSummary loopProgress={baseProgress} onNextLoop={jest.fn()} />);

    expect(screen.getByText("7")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("Correct")).toBeInTheDocument();
    expect(screen.getByText("Incorrect")).toBeInTheDocument();
  });

  it("shows accuracy percentage", () => {
    render(<LoopSummary loopProgress={baseProgress} onNextLoop={jest.fn()} />);

    expect(screen.getByText("70%")).toBeInTheDocument();
    expect(screen.getByText("Accuracy")).toBeInTheDocument();
  });

  it("calls onNextLoop when button clicked", () => {
    const onNextLoop = jest.fn();
    render(<LoopSummary loopProgress={baseProgress} onNextLoop={onNextLoop} />);

    fireEvent.click(screen.getByRole("button", { name: /next loop/i }));

    expect(onNextLoop).toHaveBeenCalledTimes(1);
  });

  it("shows loop 2 for second pass", () => {
    const loop2 = { ...baseProgress, loopNumber: 2, correct: 9, incorrect: 1 };
    render(<LoopSummary loopProgress={loop2} onNextLoop={jest.fn()} />);

    expect(screen.getByText("Loop 2 Complete")).toBeInTheDocument();
    expect(screen.getByText("90%")).toBeInTheDocument();
  });

  it("handles 0 total gracefully", () => {
    const empty = { ...baseProgress, total: 0, correct: 0, incorrect: 0 };
    render(<LoopSummary loopProgress={empty} onNextLoop={jest.fn()} />);

    expect(screen.getByText("0%")).toBeInTheDocument();
  });
});
