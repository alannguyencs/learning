import React from "react";
import { render, screen } from "@testing-library/react";
import RecallSummary from "../../components/RecallSummary";

const defaultProps = {
  globalRecall: 0.78,
  globalAccuracy: 0.85,
  topicsAtRisk: 0,
  lessonsAtRisk: 0,
};

describe("RecallSummary", () => {
  it("renders global recall percentage", () => {
    render(<RecallSummary {...defaultProps} />);
    expect(screen.getByText("78%")).toBeInTheDocument();
    expect(screen.getByText("Global Recall")).toBeInTheDocument();
  });

  it("renders quiz accuracy percentage", () => {
    render(<RecallSummary {...defaultProps} />);
    expect(screen.getByText("85%")).toBeInTheDocument();
    expect(screen.getByText("Quiz Accuracy")).toBeInTheDocument();
  });

  it("renders topics at risk count", () => {
    render(<RecallSummary {...defaultProps} topicsAtRisk={2} />);
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("Topics at Risk")).toBeInTheDocument();
  });

  it("renders lessons at risk count", () => {
    render(<RecallSummary {...defaultProps} lessonsAtRisk={5} />);
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("Lessons at Risk")).toBeInTheDocument();
  });
});
