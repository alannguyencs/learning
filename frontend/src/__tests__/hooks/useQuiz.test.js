import { renderHook, act } from "@testing-library/react";
import useQuiz from "../../hooks/useQuiz";
import apiService from "../../services/api";

jest.mock("../../services/api");

describe("useQuiz", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("initializes with idle state", () => {
    const { result } = renderHook(() => useQuiz());

    expect(result.current.loading).toBe(false);
    expect(result.current.quiz).toBeNull();
    expect(result.current.result).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.scope).toEqual({
      topicId: null,
      lessonId: null,
    });
  });

  it("fetchNextQuiz sets quiz on success", async () => {
    const mockQuiz = {
      quiz_id: 1,
      question: "What is X?",
      options: { A: "a", B: "b", C: "c", D: "d" },
      quiz_type: "recall",
      correct_option_count: 1,
    };
    apiService.getNextQuiz.mockResolvedValue(mockQuiz);

    const { result } = renderHook(() => useQuiz());

    await act(async () => {
      await result.current.fetchNextQuiz();
    });

    expect(result.current.quiz).toEqual(mockQuiz);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("fetchNextQuiz sets error on 404", async () => {
    apiService.getNextQuiz.mockRejectedValue({
      response: { status: 404 },
    });

    const { result } = renderHook(() => useQuiz());

    await act(async () => {
      await result.current.fetchNextQuiz();
    });

    expect(result.current.quiz).toBeNull();
    expect(result.current.error).toMatch(/no quiz questions/i);
  });

  it("submitAnswer sets result on success", async () => {
    const mockQuiz = { quiz_id: 1, question: "Q?" };
    apiService.getNextQuiz.mockResolvedValue(mockQuiz);
    const mockResult = {
      is_correct: true,
      correct_options: ["B"],
      quiz_learnt: "About X",
      explanations: { A: "eA", B: "eB", C: "eC", D: "eD" },
      quiz_take_away: "Takeaway",
    };
    apiService.submitAnswer.mockResolvedValue(mockResult);

    const { result } = renderHook(() => useQuiz());

    await act(async () => {
      await result.current.fetchNextQuiz();
    });

    await act(async () => {
      await result.current.submitAnswer(["B"]);
    });

    expect(result.current.result).toEqual(mockResult);
    expect(apiService.submitAnswer).toHaveBeenCalledWith(1, ["B"]);
  });

  it("submitAnswer does nothing without quiz", async () => {
    const { result } = renderHook(() => useQuiz());

    await act(async () => {
      await result.current.submitAnswer(["B"]);
    });

    expect(apiService.submitAnswer).not.toHaveBeenCalled();
  });

  it("reset clears quiz and result", async () => {
    const mockQuiz = { quiz_id: 1, question: "Q?" };
    apiService.getNextQuiz.mockResolvedValue(mockQuiz);

    const { result } = renderHook(() => useQuiz());

    await act(async () => {
      await result.current.fetchNextQuiz();
    });
    expect(result.current.quiz).not.toBeNull();

    act(() => {
      result.current.reset();
    });

    expect(result.current.quiz).toBeNull();
    expect(result.current.result).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it("setScope updates scope", () => {
    const { result } = renderHook(() => useQuiz());

    act(() => {
      result.current.setScope({ topicId: "t1", lessonId: 2 });
    });

    expect(result.current.scope).toEqual({ topicId: "t1", lessonId: 2 });
  });
});
