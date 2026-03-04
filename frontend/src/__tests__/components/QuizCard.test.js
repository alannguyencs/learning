import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import QuizCard from "../../components/QuizCard";

const singleQuiz = {
  quiz_id: 1,
  question: "What is the capital of France?",
  options: { A: "London", B: "Paris", C: "Berlin", D: "Madrid" },
  quiz_type: "recall",
  correct_option_count: 1,
};

const multiQuiz = {
  quiz_id: 2,
  question: "Which are fruits?",
  options: { A: "Apple", B: "Carrot", C: "Banana", D: "Potato" },
  quiz_type: "understanding",
  correct_option_count: 2,
};

describe("QuizCard", () => {
  it("renders question and all options", () => {
    render(<QuizCard quiz={singleQuiz} onSubmit={jest.fn()} disabled={false} />);

    expect(screen.getByText("What is the capital of France?")).toBeInTheDocument();
    expect(screen.getByText("London")).toBeInTheDocument();
    expect(screen.getByText("Paris")).toBeInTheDocument();
    expect(screen.getByText("Berlin")).toBeInTheDocument();
    expect(screen.getByText("Madrid")).toBeInTheDocument();
  });

  it("shows quiz type badge", () => {
    render(<QuizCard quiz={singleQuiz} onSubmit={jest.fn()} disabled={false} />);

    expect(screen.getByText("recall")).toBeInTheDocument();
  });

  it("single-answer submits immediately on click", () => {
    const onSubmit = jest.fn();
    render(<QuizCard quiz={singleQuiz} onSubmit={onSubmit} disabled={false} />);

    fireEvent.click(screen.getByText("Paris"));

    expect(onSubmit).toHaveBeenCalledWith(["B"]);
  });

  it("multi-answer shows select all that apply hint", () => {
    render(<QuizCard quiz={multiQuiz} onSubmit={jest.fn()} disabled={false} />);

    expect(screen.getByText(/select all that apply/i)).toBeInTheDocument();
  });

  it("multi-answer toggles selection and submits on button click", () => {
    const onSubmit = jest.fn();
    render(<QuizCard quiz={multiQuiz} onSubmit={onSubmit} disabled={false} />);

    fireEvent.click(screen.getByText("Apple"));
    fireEvent.click(screen.getByText("Banana"));
    fireEvent.click(screen.getByRole("button", { name: /submit answer/i }));

    expect(onSubmit).toHaveBeenCalledWith(["A", "C"]);
  });

  it("multi-answer submit button disabled when nothing selected", () => {
    render(<QuizCard quiz={multiQuiz} onSubmit={jest.fn()} disabled={false} />);

    expect(screen.getByRole("button", { name: /submit answer/i })).toBeDisabled();
  });

  it("does not fire onSubmit when disabled", () => {
    const onSubmit = jest.fn();
    render(<QuizCard quiz={singleQuiz} onSubmit={onSubmit} disabled={true} />);

    fireEvent.click(screen.getByText("Paris"));

    expect(onSubmit).not.toHaveBeenCalled();
  });
});
