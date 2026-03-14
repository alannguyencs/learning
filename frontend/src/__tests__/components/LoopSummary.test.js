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

const globalScope = { topicId: null, lessonId: null };
const topicScope = { topicId: "math", lessonId: null };
const lessonScope = { topicId: "math", lessonId: 5 };

describe("LoopSummary", () => {
  it("renders heading and total", () => {
    render(
      <LoopSummary
        loopProgress={baseProgress}
        onNextLoop={jest.fn()}
        scope={globalScope}
      />,
    );

    expect(screen.getByText("Loop Complete")).toBeInTheDocument();
    expect(
      screen.getByText("You answered all 10 questions"),
    ).toBeInTheDocument();
  });

  it("shows correct and incorrect counts", () => {
    render(
      <LoopSummary
        loopProgress={baseProgress}
        onNextLoop={jest.fn()}
        scope={globalScope}
      />,
    );

    expect(screen.getByText("7")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("Correct")).toBeInTheDocument();
    expect(screen.getByText("Incorrect")).toBeInTheDocument();
  });

  it("shows accuracy percentage", () => {
    render(
      <LoopSummary
        loopProgress={baseProgress}
        onNextLoop={jest.fn()}
        scope={globalScope}
      />,
    );

    expect(screen.getByText("70%")).toBeInTheDocument();
    expect(screen.getByText("Accuracy")).toBeInTheDocument();
  });

  it("global scope shows single Next Loop button", () => {
    const onNextLoop = jest.fn();
    render(
      <LoopSummary
        loopProgress={baseProgress}
        onNextLoop={onNextLoop}
        scope={globalScope}
      />,
    );

    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(1);
    expect(buttons[0]).toHaveTextContent("Next Loop");

    fireEvent.click(buttons[0]);
    expect(onNextLoop).toHaveBeenCalledWith({
      topicId: null,
      lessonId: null,
    });
  });

  it("topic scope shows topic and all-topics buttons", () => {
    const onNextLoop = jest.fn();
    render(
      <LoopSummary
        loopProgress={baseProgress}
        onNextLoop={onNextLoop}
        scope={topicScope}
        topicName="Mathematics"
      />,
    );

    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(2);
    expect(buttons[0]).toHaveTextContent("Next Loop - Mathematics");
    expect(buttons[1]).toHaveTextContent("Next Loop - All Topics");

    fireEvent.click(buttons[0]);
    expect(onNextLoop).toHaveBeenCalledWith({
      topicId: "math",
      lessonId: null,
    });

    fireEvent.click(buttons[1]);
    expect(onNextLoop).toHaveBeenCalledWith({
      topicId: null,
      lessonId: null,
    });
  });

  it("lesson scope shows lesson, topic, and all-topics buttons", () => {
    const onNextLoop = jest.fn();
    render(
      <LoopSummary
        loopProgress={baseProgress}
        onNextLoop={onNextLoop}
        scope={lessonScope}
        topicName="Mathematics"
        lessonTitle="Algebra Basics"
      />,
    );

    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(3);
    expect(buttons[0]).toHaveTextContent("Next Loop - Algebra Basics");
    expect(buttons[1]).toHaveTextContent("Next Loop - Mathematics");
    expect(buttons[2]).toHaveTextContent("Next Loop - All Topics");

    fireEvent.click(buttons[0]);
    expect(onNextLoop).toHaveBeenCalledWith({
      topicId: "math",
      lessonId: 5,
    });

    fireEvent.click(buttons[1]);
    expect(onNextLoop).toHaveBeenCalledWith({
      topicId: "math",
      lessonId: null,
    });

    fireEvent.click(buttons[2]);
    expect(onNextLoop).toHaveBeenCalledWith({
      topicId: null,
      lessonId: null,
    });
  });

  it("handles 0 total gracefully", () => {
    const empty = { ...baseProgress, total: 0, correct: 0, incorrect: 0 };
    render(
      <LoopSummary
        loopProgress={empty}
        onNextLoop={jest.fn()}
        scope={globalScope}
      />,
    );

    expect(screen.getByText("0%")).toBeInTheDocument();
  });
});
