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

  describe("loop progress tracking", () => {
    const mockQuiz = {
      quiz_id: 1,
      question: "Q?",
      options: { A: "a", B: "b", C: "c", D: "d" },
      quiz_type: "recall",
      correct_option_count: 1,
      lesson_title: "Test Lesson",
      loop_question_count: 3,
    };
    const correctResult = {
      is_correct: true,
      correct_options: ["B"],
      quiz_learnt: "X",
      explanations: { A: "eA", B: "eB", C: "eC", D: "eD" },
      quiz_take_away: "TK",
    };
    const incorrectResult = { ...correctResult, is_correct: false };

    it("initializes loopProgress", () => {
      const { result } = renderHook(() => useQuiz());

      expect(result.current.loopProgress).toEqual({
        answered: 0,
        correct: 0,
        incorrect: 0,
        loopNumber: 1,
        total: 0,
        loopComplete: false,
        results: [],
      });
    });

    it("sets total from loop_question_count", async () => {
      apiService.getNextQuiz.mockResolvedValue(mockQuiz);

      const { result } = renderHook(() => useQuiz());

      await act(async () => {
        await result.current.fetchNextQuiz();
      });

      expect(result.current.loopProgress.total).toBe(3);
    });

    it("increments answered and correct on correct answer", async () => {
      apiService.getNextQuiz.mockResolvedValue(mockQuiz);
      apiService.submitAnswer.mockResolvedValue(correctResult);

      const { result } = renderHook(() => useQuiz());

      act(() => {
        result.current.setScope({ topicId: null, lessonId: 5 });
      });

      await act(async () => {
        await result.current.fetchNextQuiz();
      });

      await act(async () => {
        await result.current.submitAnswer(["B"]);
      });

      expect(result.current.loopProgress.answered).toBe(1);
      expect(result.current.loopProgress.correct).toBe(1);
      expect(result.current.loopProgress.incorrect).toBe(0);
      expect(result.current.loopProgress.results).toEqual(["correct"]);
    });

    it("increments incorrect on wrong answer", async () => {
      apiService.getNextQuiz.mockResolvedValue(mockQuiz);
      apiService.submitAnswer.mockResolvedValue(incorrectResult);

      const { result } = renderHook(() => useQuiz());

      act(() => {
        result.current.setScope({ topicId: null, lessonId: 5 });
      });

      await act(async () => {
        await result.current.fetchNextQuiz();
      });

      await act(async () => {
        await result.current.submitAnswer(["A"]);
      });

      expect(result.current.loopProgress.incorrect).toBe(1);
      expect(result.current.loopProgress.correct).toBe(0);
      expect(result.current.loopProgress.results).toEqual(["incorrect"]);
    });

    it("sets loopComplete when answered equals total", async () => {
      apiService.getNextQuiz.mockResolvedValue(mockQuiz);
      apiService.submitAnswer.mockResolvedValue(correctResult);

      const { result } = renderHook(() => useQuiz());

      act(() => {
        result.current.setScope({ topicId: null, lessonId: 5 });
      });

      // Answer 3 quizzes (total = 3)
      for (let i = 0; i < 3; i++) {
        await act(async () => {
          await result.current.fetchNextQuiz();
        });
        await act(async () => {
          await result.current.submitAnswer(["B"]);
        });
      }

      expect(result.current.loopProgress.loopComplete).toBe(true);
      expect(result.current.loopProgress.answered).toBe(3);
    });

    it("startNextLoop resets counters, increments loopNumber, and fetches next quiz", async () => {
      apiService.getNextQuiz.mockResolvedValue(mockQuiz);
      apiService.submitAnswer.mockResolvedValue(correctResult);

      const { result } = renderHook(() => useQuiz());

      act(() => {
        result.current.setScope({ topicId: null, lessonId: 5 });
      });

      // Complete a loop
      for (let i = 0; i < 3; i++) {
        await act(async () => {
          await result.current.fetchNextQuiz();
        });
        await act(async () => {
          await result.current.submitAnswer(["B"]);
        });
      }

      expect(result.current.loopProgress.loopComplete).toBe(true);

      await act(async () => {
        await result.current.startNextLoop();
      });

      expect(result.current.loopProgress.loopNumber).toBe(2);
      expect(result.current.loopProgress.answered).toBe(0);
      expect(result.current.loopProgress.correct).toBe(0);
      expect(result.current.loopProgress.loopComplete).toBe(false);
      expect(result.current.loopProgress.total).toBe(3);
      expect(result.current.loopProgress.results).toEqual([]);
      expect(result.current.quiz).toEqual(mockQuiz);
    });

    it("reset clears loopProgress entirely", async () => {
      apiService.getNextQuiz.mockResolvedValue(mockQuiz);
      apiService.submitAnswer.mockResolvedValue(correctResult);

      const { result } = renderHook(() => useQuiz());

      act(() => {
        result.current.setScope({ topicId: null, lessonId: 5 });
      });

      await act(async () => {
        await result.current.fetchNextQuiz();
      });
      await act(async () => {
        await result.current.submitAnswer(["B"]);
      });

      act(() => {
        result.current.reset();
      });

      expect(result.current.loopProgress).toEqual({
        answered: 0,
        correct: 0,
        incorrect: 0,
        loopNumber: 1,
        total: 0,
        loopComplete: false,
        results: [],
      });
    });

    it("tracks loop progress for all scopes", async () => {
      apiService.getNextQuiz.mockResolvedValue(mockQuiz);
      apiService.submitAnswer.mockResolvedValue(correctResult);

      const { result } = renderHook(() => useQuiz());

      // No lessonId in scope — loop tracking still works
      await act(async () => {
        await result.current.fetchNextQuiz();
      });
      await act(async () => {
        await result.current.submitAnswer(["B"]);
      });

      expect(result.current.loopProgress.answered).toBe(1);
    });

    it("skipQuestion adds skipped to results and increments answered", async () => {
      apiService.getNextQuiz.mockResolvedValue(mockQuiz);

      const { result } = renderHook(() => useQuiz());

      act(() => {
        result.current.setScope({ topicId: null, lessonId: 5 });
      });

      await act(async () => {
        await result.current.fetchNextQuiz();
      });

      act(() => {
        result.current.skipQuestion();
      });

      expect(result.current.loopProgress.answered).toBe(1);
      expect(result.current.loopProgress.results).toEqual(["skipped"]);
      expect(result.current.loopProgress.correct).toBe(0);
      expect(result.current.loopProgress.incorrect).toBe(0);
    });

    it("skipQuestion sets loopComplete when all questions skipped", async () => {
      apiService.getNextQuiz.mockResolvedValue(mockQuiz);

      const { result } = renderHook(() => useQuiz());

      act(() => {
        result.current.setScope({ topicId: null, lessonId: 5 });
      });

      await act(async () => {
        await result.current.fetchNextQuiz();
      });

      // Skip all 3 questions (total = 3 from mockQuiz.lesson_question_count)
      for (let i = 0; i < 3; i++) {
        act(() => {
          result.current.skipQuestion();
        });
      }

      expect(result.current.loopProgress.loopComplete).toBe(true);
      expect(result.current.loopProgress.results).toEqual([
        "skipped",
        "skipped",
        "skipped",
      ]);
    });

    it("skipQuestion works for all scopes", async () => {
      const { result } = renderHook(() => useQuiz());

      act(() => {
        result.current.skipQuestion();
      });

      expect(result.current.loopProgress.answered).toBe(1);
      expect(result.current.loopProgress.results).toEqual(["skipped"]);
    });

    it("tracks mixed answered and skipped results", async () => {
      apiService.getNextQuiz.mockResolvedValue(mockQuiz);
      apiService.submitAnswer.mockResolvedValue(correctResult);

      const { result } = renderHook(() => useQuiz());

      act(() => {
        result.current.setScope({ topicId: null, lessonId: 5 });
      });

      // Answer first quiz
      await act(async () => {
        await result.current.fetchNextQuiz();
      });
      await act(async () => {
        await result.current.submitAnswer(["B"]);
      });

      // Skip second quiz
      act(() => {
        result.current.skipQuestion();
      });

      // Answer third quiz
      apiService.submitAnswer.mockResolvedValue(incorrectResult);
      await act(async () => {
        await result.current.fetchNextQuiz();
      });
      await act(async () => {
        await result.current.submitAnswer(["A"]);
      });

      expect(result.current.loopProgress.results).toEqual([
        "correct",
        "skipped",
        "incorrect",
      ]);
      expect(result.current.loopProgress.loopComplete).toBe(true);
      expect(result.current.loopProgress.correct).toBe(1);
      expect(result.current.loopProgress.incorrect).toBe(1);
      expect(result.current.loopProgress.answered).toBe(3);
    });
  });
});
