import { renderHook, act } from "@testing-library/react";
import useDashboardData from "../../hooks/useDashboardData";
import apiService from "../../services/api";

jest.mock("../../services/api");

const mockRecallMap = {
  topics: [
    {
      topic_id: "t1",
      topic_name: "Topic One",
      lesson_count: 2,
      recall_probability: 0.85,
      forgetting_rate: 0.2,
      last_review_at: null,
      review_count: 5,
      correct_count: 4,
      lessons: [],
    },
  ],
  global_recall: 0.85,
  topics_at_risk: 0,
  lessons_at_risk: 0,
};

const mockTopicMatrix = {
  topics: [
    {
      topic_id: "t1",
      topic_name: "Topic One",
      lesson_count: 2,
      last_quiz_at: null,
      quizzes: [],
    },
  ],
  max_quiz_count: 0,
};

describe("useDashboardData hook", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("fetches recall map and topic matrix on mount", async () => {
    apiService.getRecallMap.mockResolvedValue(mockRecallMap);
    apiService.getTopicMatrix.mockResolvedValue(mockTopicMatrix);

    const { result } = renderHook(() => useDashboardData());

    // Initially loading
    expect(result.current.loading).toBe(true);

    await act(async () => {});

    expect(result.current.loading).toBe(false);
    expect(result.current.recallMap).toEqual(mockRecallMap);
    expect(result.current.topicMatrix).toEqual(mockTopicMatrix);
    expect(apiService.getRecallMap).toHaveBeenCalledTimes(1);
    expect(apiService.getTopicMatrix).toHaveBeenCalledTimes(1);
  });

  it("manages expandedTopics state", async () => {
    apiService.getRecallMap.mockResolvedValue(mockRecallMap);
    apiService.getTopicMatrix.mockResolvedValue(mockTopicMatrix);

    const { result } = renderHook(() => useDashboardData());
    await act(async () => {});

    expect(result.current.expandedTopics.size).toBe(0);

    act(() => {
      result.current.toggleTopic("t1");
    });
    expect(result.current.expandedTopics.has("t1")).toBe(true);

    act(() => {
      result.current.toggleTopic("t1");
    });
    expect(result.current.expandedTopics.has("t1")).toBe(false);
  });

  it("handles loading state", async () => {
    apiService.getRecallMap.mockResolvedValue(mockRecallMap);
    apiService.getTopicMatrix.mockResolvedValue(mockTopicMatrix);

    const { result } = renderHook(() => useDashboardData());
    expect(result.current.loading).toBe(true);

    await act(async () => {});
    expect(result.current.loading).toBe(false);
  });

  it("handles API error", async () => {
    apiService.getRecallMap.mockRejectedValue(new Error("Network error"));
    apiService.getTopicMatrix.mockRejectedValue(new Error("Network error"));

    const { result } = renderHook(() => useDashboardData());
    await act(async () => {});

    expect(result.current.error).toBe("Failed to load dashboard data.");
    expect(result.current.recallMap).toBeNull();
  });
});
