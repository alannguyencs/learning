import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import TopicLessonFilter from "../../components/TopicLessonFilter";
import apiService from "../../services/api";

jest.mock("../../services/api");

const mockTopics = {
  topics: [
    {
      topic_id: "t1",
      topic_name: "Topic 1",
      lessons: [
        { lesson_id: 1, lesson_name: "Lesson A" },
        { lesson_id: 2, lesson_name: "Lesson B" },
      ],
    },
    {
      topic_id: "t2",
      topic_name: "Topic 2",
      lessons: [{ lesson_id: 3, lesson_name: "Lesson C" }],
    },
  ],
};

describe("TopicLessonFilter", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    apiService.getQuizTopics.mockResolvedValue(mockTopics);
  });

  it("renders All Topics option by default", async () => {
    render(
      <TopicLessonFilter
        scope={{ topicId: null, lessonId: null }}
        onScopeChange={jest.fn()}
      />,
    );

    await waitFor(() => {
      expect(screen.getByDisplayValue("All Topics")).toBeInTheDocument();
    });
  });

  it("shows topics from API", async () => {
    render(
      <TopicLessonFilter
        scope={{ topicId: null, lessonId: null }}
        onScopeChange={jest.fn()}
      />,
    );

    await waitFor(() => {
      expect(screen.getByText("Topic 1")).toBeInTheDocument();
      expect(screen.getByText("Topic 2")).toBeInTheDocument();
    });
  });

  it("calls onScopeChange with topic_id on topic select", async () => {
    const onScopeChange = jest.fn();
    render(
      <TopicLessonFilter
        scope={{ topicId: null, lessonId: null }}
        onScopeChange={onScopeChange}
      />,
    );

    await waitFor(() => {
      expect(screen.getByText("Topic 1")).toBeInTheDocument();
    });

    fireEvent.change(screen.getByDisplayValue("All Topics"), {
      target: { value: "t1" },
    });

    expect(onScopeChange).toHaveBeenCalledWith({
      topicId: "t1",
      lessonId: null,
    });
  });

  it("shows lesson dropdown when topic is selected", async () => {
    const onScopeChange = jest.fn();
    render(
      <TopicLessonFilter
        scope={{ topicId: null, lessonId: null }}
        onScopeChange={onScopeChange}
      />,
    );

    await waitFor(() => {
      expect(screen.getByText("Topic 1")).toBeInTheDocument();
    });

    fireEvent.change(screen.getByDisplayValue("All Topics"), {
      target: { value: "t1" },
    });

    expect(screen.getByText("Lesson A")).toBeInTheDocument();
    expect(screen.getByText("Lesson B")).toBeInTheDocument();
  });

  it("calls onScopeChange with lesson_id on lesson select", async () => {
    const onScopeChange = jest.fn();
    render(
      <TopicLessonFilter
        scope={{ topicId: null, lessonId: null }}
        onScopeChange={onScopeChange}
      />,
    );

    await waitFor(() => {
      expect(screen.getByText("Topic 1")).toBeInTheDocument();
    });

    fireEvent.change(screen.getByDisplayValue("All Topics"), {
      target: { value: "t1" },
    });

    fireEvent.change(screen.getByDisplayValue("All Lessons"), {
      target: { value: "2" },
    });

    expect(onScopeChange).toHaveBeenLastCalledWith({
      topicId: "t1",
      lessonId: 2,
    });
  });
});
