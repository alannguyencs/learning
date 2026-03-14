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
  it("shows correct option explanation when answer is correct", () => {
    render(<QuizResult result={correctResult} userAnswer={["B"]} />);

    expect(
      screen.getByText("Paris is indeed the capital of France"),
    ).toBeInTheDocument();
  });

  it("shows wrong selection explanation when answer is incorrect", () => {
    render(<QuizResult result={incorrectResult} userAnswer={["A"]} />);

    expect(
      screen.getByText("London is the capital of the UK"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Paris is indeed the capital of France"),
    ).toBeInTheDocument();
  });

  it("does not show wrong selections section when correct", () => {
    const { container } = render(
      <QuizResult result={correctResult} userAnswer={["B"]} />,
    );

    const redBorders = container.querySelectorAll(".border-red-500\\/30");
    expect(redBorders.length).toBe(0);
  });

  it("displays quiz_take_away", () => {
    render(<QuizResult result={correctResult} userAnswer={["B"]} />);

    expect(
      screen.getByText("European capitals are important to know"),
    ).toBeInTheDocument();
  });

  it("displays Key Takeaway heading", () => {
    render(<QuizResult result={correctResult} userAnswer={["B"]} />);

    expect(screen.getByText("Key Takeaway")).toBeInTheDocument();
  });
});
