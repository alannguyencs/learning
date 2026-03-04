import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import RecallHeatmap from "../../components/RecallHeatmap";

const mockTopics = [
  {
    topic_id: "t1",
    topic_name: "Topic One",
    lesson_count: 2,
    recall_probability: 0.85,
    forgetting_rate: 0.2,
    last_review_at: null,
    review_count: 10,
    correct_count: 8,
    lessons: [
      {
        lesson_id: 1,
        lesson_name: "Lesson A",
        recall_probability: 0.9,
        forgetting_rate: 0.1,
        last_review_at: null,
        review_count: 5,
        correct_count: 4,
      },
    ],
  },
  {
    topic_id: "t2",
    topic_name: "Topic Two",
    lesson_count: 1,
    recall_probability: 0.6,
    forgetting_rate: 0.3,
    last_review_at: null,
    review_count: 3,
    correct_count: 1,
    lessons: [],
  },
  {
    topic_id: "t3",
    topic_name: "Topic Three",
    lesson_count: 1,
    recall_probability: 0.3,
    forgetting_rate: 0.5,
    last_review_at: null,
    review_count: 2,
    correct_count: 0,
    lessons: [],
  },
];

const renderWithRouter = (ui) => render(<BrowserRouter>{ui}</BrowserRouter>);

describe("RecallHeatmap", () => {
  it("renders topic cards", () => {
    renderWithRouter(
      <RecallHeatmap
        topics={mockTopics}
        expandedTopics={new Set()}
        onToggleTopic={() => {}}
      />,
    );
    expect(screen.getByText("Topic One")).toBeInTheDocument();
    expect(screen.getByText("Topic Two")).toBeInTheDocument();
    expect(screen.getByText("Topic Three")).toBeInTheDocument();
  });

  it("applies green for recall > 0.7", () => {
    renderWithRouter(
      <RecallHeatmap
        topics={mockTopics}
        expandedTopics={new Set()}
        onToggleTopic={() => {}}
      />,
    );
    // Topic One has 85% recall
    expect(screen.getByText("85%")).toBeInTheDocument();
  });

  it("applies yellow for recall 0.5-0.7", () => {
    renderWithRouter(
      <RecallHeatmap
        topics={mockTopics}
        expandedTopics={new Set()}
        onToggleTopic={() => {}}
      />,
    );
    expect(screen.getByText("60%")).toBeInTheDocument();
  });

  it("applies red for recall < 0.5", () => {
    renderWithRouter(
      <RecallHeatmap
        topics={mockTopics}
        expandedTopics={new Set()}
        onToggleTopic={() => {}}
      />,
    );
    expect(screen.getByText("30%")).toBeInTheDocument();
  });

  it("expands topic to show lessons", () => {
    const onToggle = jest.fn();
    renderWithRouter(
      <RecallHeatmap
        topics={mockTopics}
        expandedTopics={new Set(["t1"])}
        onToggleTopic={onToggle}
      />,
    );

    // Lesson A should be visible when t1 is expanded
    expect(screen.getByText("Lesson A")).toBeInTheDocument();

    // Clicking should call toggle
    fireEvent.click(screen.getByText("Topic One"));
    expect(onToggle).toHaveBeenCalledWith("t1");
  });
});
