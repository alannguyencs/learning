import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import QuizCard from "../../components/QuizCard";

const renderWithRouter = (ui) => render(<BrowserRouter>{ui}</BrowserRouter>);

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
    renderWithRouter(
      <QuizCard quiz={singleQuiz} onSubmit={jest.fn()} disabled={false} />,
    );

    expect(
      screen.getByText("What is the capital of France?"),
    ).toBeInTheDocument();
    expect(screen.getByText("London")).toBeInTheDocument();
    expect(screen.getByText("Paris")).toBeInTheDocument();
    expect(screen.getByText("Berlin")).toBeInTheDocument();
    expect(screen.getByText("Madrid")).toBeInTheDocument();
  });

  it("shows quiz type badge", () => {
    renderWithRouter(
      <QuizCard quiz={singleQuiz} onSubmit={jest.fn()} disabled={false} />,
    );

    expect(screen.getByText("recall")).toBeInTheDocument();
  });

  it("single-answer submits immediately on click", () => {
    const onSubmit = jest.fn();
    renderWithRouter(
      <QuizCard quiz={singleQuiz} onSubmit={onSubmit} disabled={false} />,
    );

    fireEvent.click(screen.getByText("Paris"));

    expect(onSubmit).toHaveBeenCalledWith(["B"]);
  });

  it("multi-answer shows select all that apply hint", () => {
    renderWithRouter(
      <QuizCard quiz={multiQuiz} onSubmit={jest.fn()} disabled={false} />,
    );

    expect(screen.getByText(/select all that apply/i)).toBeInTheDocument();
  });

  it("multi-answer toggles selection and submits on button click", () => {
    const onSubmit = jest.fn();
    renderWithRouter(
      <QuizCard quiz={multiQuiz} onSubmit={onSubmit} disabled={false} />,
    );

    fireEvent.click(screen.getByText("Apple"));
    fireEvent.click(screen.getByText("Banana"));
    fireEvent.click(screen.getByRole("button", { name: /submit answer/i }));

    expect(onSubmit).toHaveBeenCalledWith(["A", "C"]);
  });

  it("multi-answer submit button disabled when nothing selected", () => {
    renderWithRouter(
      <QuizCard quiz={multiQuiz} onSubmit={jest.fn()} disabled={false} />,
    );

    expect(
      screen.getByRole("button", { name: /submit answer/i }),
    ).toBeDisabled();
  });

  it("does not fire onSubmit when disabled", () => {
    const onSubmit = jest.fn();
    renderWithRouter(
      <QuizCard quiz={singleQuiz} onSubmit={onSubmit} disabled={true} />,
    );

    fireEvent.click(screen.getByText("Paris"));

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("shows progress squares when totalQuestions is provided", () => {
    const { container } = renderWithRouter(
      <QuizCard
        quiz={singleQuiz}
        onSubmit={jest.fn()}
        disabled={false}
        totalQuestions={4}
        loopResults={["correct", "incorrect"]}
      />,
    );

    const squares = container.querySelectorAll(".w-3.h-3.rounded-sm");
    expect(squares).toHaveLength(4);
    expect(squares[0].className).toContain("bg-green-500");
    expect(squares[1].className).toContain("bg-red-500");
    expect(squares[2].className).toContain("bg-gray-500");
    expect(squares[3].className).toContain("bg-gray-500");
  });

  it("shows yellow square for skipped questions", () => {
    const { container } = renderWithRouter(
      <QuizCard
        quiz={singleQuiz}
        onSubmit={jest.fn()}
        disabled={false}
        totalQuestions={3}
        loopResults={["correct", "skipped", "incorrect"]}
      />,
    );

    const squares = container.querySelectorAll(".w-3.h-3.rounded-sm");
    expect(squares).toHaveLength(3);
    expect(squares[0].className).toContain("bg-green-500");
    expect(squares[1].className).toContain("bg-yellow-500");
    expect(squares[2].className).toContain("bg-red-500");
  });

  it("hides progress squares when totalQuestions is not provided", () => {
    const { container } = renderWithRouter(
      <QuizCard quiz={singleQuiz} onSubmit={jest.fn()} disabled={false} />,
    );

    const squares = container.querySelectorAll(".w-3.h-3.rounded-sm");
    expect(squares).toHaveLength(0);
  });
});
