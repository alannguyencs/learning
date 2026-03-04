import React from "react";
import { render, screen } from "@testing-library/react";
import RecallSummary from "../../components/RecallSummary";

describe("RecallSummary", () => {
  it("renders global recall percentage", () => {
    render(
      <RecallSummary
        globalRecall={0.78}
        topicsAtRisk={0}
        lessonsAtRisk={0}
      />,
    );
    expect(screen.getByText("78%")).toBeInTheDocument();
    expect(screen.getByText("Global Recall")).toBeInTheDocument();
  });

  it("renders topics at risk count", () => {
    render(
      <RecallSummary
        globalRecall={0.5}
        topicsAtRisk={2}
        lessonsAtRisk={0}
      />,
    );
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("Topics at Risk")).toBeInTheDocument();
  });

  it("renders lessons at risk count", () => {
    render(
      <RecallSummary
        globalRecall={0.5}
        topicsAtRisk={0}
        lessonsAtRisk={5}
      />,
    );
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("Lessons at Risk")).toBeInTheDocument();
  });
});
