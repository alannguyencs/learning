import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import QuizLaunchButton from "../../components/QuizLaunchButton";

const mockNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
}));

describe("QuizLaunchButton", () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it("navigates to /quiz with topicId", () => {
    render(
      <BrowserRouter>
        <QuizLaunchButton topicId="t1" />
      </BrowserRouter>,
    );

    fireEvent.click(screen.getByText("Quiz"));
    expect(mockNavigate).toHaveBeenCalledWith("/quiz?topicId=t1");
  });

  it("navigates to /quiz with lessonId", () => {
    render(
      <BrowserRouter>
        <QuizLaunchButton topicId="t1" lessonId={2} />
      </BrowserRouter>,
    );

    fireEvent.click(screen.getByText("Quiz"));
    expect(mockNavigate).toHaveBeenCalledWith("/quiz?topicId=t1&lessonId=2");
  });
});
