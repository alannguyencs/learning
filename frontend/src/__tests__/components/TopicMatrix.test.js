import React from "react";
import { render, screen } from "@testing-library/react";
import TopicMatrix from "../../components/TopicMatrix";

const mockTopics = [
  {
    topic_id: "t1",
    topic_name: "Topic One",
    lesson_count: 2,
    last_quiz_at: "2025-01-01T00:00:00",
    quizzes: [
      {
        quiz_id: 1,
        result: "correct",
        asked_at: "2025-01-01T00:00:00",
        column_index: 1,
        lesson_name: "Lesson A",
      },
      {
        quiz_id: 2,
        result: "incorrect",
        asked_at: "2025-01-02T00:00:00",
        column_index: 2,
        lesson_name: "Lesson B",
      },
    ],
  },
  {
    topic_id: "t2",
    topic_name: "Topic Two",
    lesson_count: 1,
    last_quiz_at: "2025-01-03T00:00:00",
    quizzes: [
      {
        quiz_id: 3,
        result: "correct",
        asked_at: "2025-01-03T00:00:00",
        column_index: 3,
        lesson_name: "Lesson C",
      },
    ],
  },
];

describe("TopicMatrix", () => {
  it("renders topic rows", () => {
    render(<TopicMatrix topics={mockTopics} maxQuizCount={3} />);
    expect(screen.getByText("Topic One")).toBeInTheDocument();
    expect(screen.getByText("Topic Two")).toBeInTheDocument();
  });

  it("renders quiz cells with colors", () => {
    const { container } = render(
      <TopicMatrix topics={mockTopics} maxQuizCount={3} />,
    );
    const greenCells = container.querySelectorAll(".bg-green-500");
    const redCells = container.querySelectorAll(".bg-red-500");
    expect(greenCells.length).toBe(2); // quiz 1 and quiz 3
    expect(redCells.length).toBe(1); // quiz 2
  });

  it("shows lesson name in tooltip", () => {
    const { container } = render(
      <TopicMatrix topics={mockTopics} maxQuizCount={3} />,
    );
    const cells = container.querySelectorAll("[title]");
    const titles = Array.from(cells).map((c) => c.getAttribute("title"));
    expect(titles.some((t) => t.includes("Lesson A"))).toBe(true);
    expect(titles.some((t) => t.includes("Lesson B"))).toBe(true);
  });
});
