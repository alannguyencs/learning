import { useState, useCallback } from "react";
import apiService from "../services/api";

const INITIAL_LOOP = {
  answered: 0,
  correct: 0,
  incorrect: 0,
  loopNumber: 1,
  total: 0,
  loopComplete: false,
  results: [],
};

const useQuiz = () => {
  const [loading, setLoading] = useState(false);
  const [quiz, setQuiz] = useState(null);
  const [result, setResult] = useState(null);
  const [userAnswer, setUserAnswer] = useState(null);
  const [error, setError] = useState(null);
  const [scope, setScope] = useState({ topicId: null, lessonId: null });
  const [loopProgress, setLoopProgress] = useState(INITIAL_LOOP);

  const fetchNextQuiz = useCallback(
    async (scopeOverride) => {
      const s = scopeOverride || scope;
      setLoading(true);
      setError(null);
      setResult(null);
      setQuiz(null);

      try {
        const data = await apiService.getNextQuiz(s.topicId, s.lessonId);
        setQuiz(data);
        if (data.loop_question_count) {
          setLoopProgress((prev) => ({
            ...prev,
            total: data.loop_question_count,
          }));
        }
      } catch (err) {
        if (err.response?.status === 404) {
          setError("No quiz questions available for this selection.");
        } else {
          setError("Failed to load quiz. Please try again.");
        }
      } finally {
        setLoading(false);
      }
    },
    [scope],
  );

  const submitAnswer = useCallback(
    async (answer) => {
      if (!quiz) return;
      setLoading(true);
      setError(null);

      try {
        setUserAnswer(answer);
        const data = await apiService.submitAnswer(quiz.quiz_id, answer);
        setResult(data);

        setLoopProgress((prev) => {
          const newAnswered = prev.answered + 1;
          return {
            ...prev,
            answered: newAnswered,
            correct: prev.correct + (data.is_correct ? 1 : 0),
            incorrect: prev.incorrect + (data.is_correct ? 0 : 1),
            loopComplete: prev.total > 0 && newAnswered >= prev.total,
            results: [
              ...prev.results,
              data.is_correct ? "correct" : "incorrect",
            ],
          };
        });
      } catch (err) {
        if (err.response?.status === 400) {
          setError("This quiz has already been answered.");
        } else {
          setError("Failed to submit answer. Please try again.");
        }
      } finally {
        setLoading(false);
      }
    },
    [quiz],
  );

  const startNextLoop = useCallback(
    async (scopeOverride) => {
      const s = scopeOverride || scope;
      setLoopProgress((prev) => ({
        ...INITIAL_LOOP,
        total: prev.total,
        loopNumber: prev.loopNumber + 1,
      }));
      setResult(null);
      setQuiz(null);
      setUserAnswer(null);
      setError(null);

      setLoading(true);
      try {
        const data = await apiService.getNextQuiz(s.topicId, s.lessonId);
        setQuiz(data);
      } catch (err) {
        if (err.response?.status === 404) {
          setError("No quiz questions available for this selection.");
        } else {
          setError("Failed to load quiz. Please try again.");
        }
      } finally {
        setLoading(false);
      }
    },
    [scope],
  );

  const skipQuestion = useCallback(() => {
    setLoopProgress((prev) => {
      const newAnswered = prev.answered + 1;
      return {
        ...prev,
        answered: newAnswered,
        loopComplete: prev.total > 0 && newAnswered >= prev.total,
        results: [...prev.results, "skipped"],
      };
    });
  }, []);

  const reset = useCallback(() => {
    setQuiz(null);
    setResult(null);
    setUserAnswer(null);
    setError(null);
    setLoopProgress(INITIAL_LOOP);
  }, []);

  return {
    loading,
    quiz,
    result,
    userAnswer,
    error,
    scope,
    setScope,
    fetchNextQuiz,
    submitAnswer,
    skipQuestion,
    startNextLoop,
    loopProgress,
    reset,
  };
};

export default useQuiz;
