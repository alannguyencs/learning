import React from "react";
import { render, screen } from "@testing-library/react";
import QuizResult from "../../components/QuizResult";

const correctResult = {
  is_correct: true,
  correct_options: ["B"],
  quiz_learnt: "Paris is the capital of France",
  explanations: {
    A: "London is the capital of the UK",
    B: "Paris is indeed the capital of France",
    C: "Berlin is the capital of Germany",
    D: "Madrid is the capital of Spain",
  },
  quiz_take_away: "European capitals are important to know",
};

const incorrectResult = {
  is_correct: false,
  correct_options: ["B"],
  quiz_learnt: "Paris is the capital of France",
  explanations: {
    A: "London is the capital of the UK",
    B: "Paris is indeed the capital of France",
    C: "Berlin is the capital of Germany",
    D: "Madrid is the capital of Spain",
  },
  quiz_take_away: "European capitals are important to know",
};

describe("QuizResult", () => {
  it("shows correct badge when answer is correct", () => {
    render(<QuizResult result={correctResult} />);

    expect(screen.getByText("Correct!")).toBeInTheDocument();
  });

  it("shows incorrect badge with correct options", () => {
    render(<QuizResult result={incorrectResult} />);

    expect(screen.getByText("Incorrect")).toBeInTheDocument();
    expect(screen.getByText(/Correct: B/)).toBeInTheDocument();
  });

  it("displays quiz_learnt section", () => {
    render(<QuizResult result={correctResult} />);

    expect(screen.getByText("Paris is the capital of France")).toBeInTheDocument();
  });

  it("displays all 4 explanations", () => {
    render(<QuizResult result={correctResult} />);

    expect(screen.getByText("London is the capital of the UK")).toBeInTheDocument();
    expect(screen.getByText("Paris is indeed the capital of France")).toBeInTheDocument();
    expect(screen.getByText("Berlin is the capital of Germany")).toBeInTheDocument();
    expect(screen.getByText("Madrid is the capital of Spain")).toBeInTheDocument();
  });

  it("displays quiz_take_away", () => {
    render(<QuizResult result={correctResult} />);

    expect(
      screen.getByText("European capitals are important to know"),
    ).toBeInTheDocument();
  });
});
