import { useState, useCallback } from "react";
import apiService from "../services/api";

const useQuiz = () => {
  const [loading, setLoading] = useState(false);
  const [quiz, setQuiz] = useState(null);
  const [result, setResult] = useState(null);
  const [userAnswer, setUserAnswer] = useState(null);
  const [error, setError] = useState(null);
  const [scope, setScope] = useState({ topicId: null, lessonId: null });

  const fetchNextQuiz = useCallback(async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    setQuiz(null);

    try {
      const data = await apiService.getNextQuiz(
        scope.topicId,
        scope.lessonId,
      );
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
  }, [scope]);

  const submitAnswer = useCallback(
    async (answer) => {
      if (!quiz) return;
      setLoading(true);
      setError(null);

      try {
        setUserAnswer(answer);
        const data = await apiService.submitAnswer(quiz.quiz_id, answer);
        setResult(data);
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

  const reset = useCallback(() => {
    setQuiz(null);
    setResult(null);
    setUserAnswer(null);
    setError(null);
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
    reset,
  };
};

export default useQuiz;
