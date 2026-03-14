import React, { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import useQuiz from "../hooks/useQuiz";
import TopicLessonFilter from "../components/TopicLessonFilter";
import QuizCard from "../components/QuizCard";
import QuizResult from "../components/QuizResult";
import LoopSummary from "../components/LoopSummary";

const QuizPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const autoFetchRef = useRef(false);
  const [showingSummary, setShowingSummary] = useState(false);
  const [loopMeta, setLoopMeta] = useState({
    topicName: null,
    lessonTitle: null,
  });
  const {
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
  } = useQuiz();

  useEffect(() => {
    const lessonId = searchParams.get("lessonId");
    if (lessonId) {
      setScope({ topicId: null, lessonId: parseInt(lessonId, 10) });
    }
    autoFetchRef.current = true;
  }, [searchParams, setScope]);

  useEffect(() => {
    if (autoFetchRef.current) {
      autoFetchRef.current = false;
      fetchNextQuiz();
    }
  }, [scope, fetchNextQuiz]);

  // Capture topic/lesson names from quiz response for LoopSummary
  // Also backfill scope.topicId when arriving via ?lessonId= URL param
  useEffect(() => {
    if (quiz) {
      setLoopMeta({
        topicName: quiz.topic_name || null,
        lessonTitle: quiz.lesson_title || null,
      });
      if (scope.lessonId && !scope.topicId && quiz.topic_id) {
        setScope((prev) => ({ ...prev, topicId: quiz.topic_id }));
      }
    }
  }, [quiz, scope.lessonId, scope.topicId, setScope]);

  const handleScopeChange = (newScope) => {
    setScope(newScope);
    setShowingSummary(false);
    setLoopMeta({ topicName: null, lessonTitle: null });
    reset();
    autoFetchRef.current = true;
  };

  const handleNextQuiz = () => {
    if (loopProgress.loopComplete && result) {
      setShowingSummary(true);
      return;
    }

    // Track skip if quiz was not answered
    if (quiz && !result && loopProgress.total > 0) {
      skipQuestion();
      // Check if skip completes the loop
      if (
        loopProgress.total > 0 &&
        loopProgress.answered + 1 >= loopProgress.total
      ) {
        setShowingSummary(true);
        return;
      }
    }

    fetchNextQuiz();
  };

  const handleNextLoop = (newScope) => {
    setShowingSummary(false);
    const sameScope =
      newScope.topicId === scope.topicId &&
      newScope.lessonId === scope.lessonId;

    if (sameScope) {
      startNextLoop();
    } else {
      setScope(newScope);
      setLoopMeta({ topicName: null, lessonTitle: null });
      reset();
      startNextLoop(newScope);
    }
  };

  return (
    <div className="min-h-screen bg-gray-800 p-8">
      <div className="max-w-3xl mx-auto mt-[22.5rem]">
        <div className="mb-6 space-y-3">
          <TopicLessonFilter scope={scope} onScopeChange={handleScopeChange} />
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigate("/dashboard")}
              className="px-4 py-2 rounded border border-gray-500 text-gray-300 hover:bg-gray-600 hover:text-white transition-colors text-sm font-medium"
            >
              Dashboard
            </button>
            {!showingSummary && (
              <button
                onClick={handleNextQuiz}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Loading..." : "Next Quiz"}
              </button>
            )}
          </div>
        </div>

        {quiz?.lesson_title && (
          <p className="mb-4 text-sm text-gray-400 truncate">
            <span className="text-gray-500">Lesson:</span>{" "}
            <a
              href={`/lessons/${quiz.lesson_id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 hover:underline transition-colors"
            >
              {quiz.lesson_title}
            </a>
          </p>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-500/20 text-red-400 rounded-lg border border-red-500/30">
            {error}
          </div>
        )}

        {showingSummary ? (
          <LoopSummary
            loopProgress={loopProgress}
            onNextLoop={handleNextLoop}
            scope={scope}
            topicName={loopMeta.topicName}
            lessonTitle={loopMeta.lessonTitle}
          />
        ) : (
          <>
            {quiz && (
              <QuizCard
                key={quiz.quiz_id}
                quiz={quiz}
                onSubmit={submitAnswer}
                disabled={loading || !!result}
                result={result}
                userAnswer={userAnswer}
                totalQuestions={
                  loopProgress.total > 0 ? loopProgress.total : null
                }
                loopResults={loopProgress.results}
              />
            )}

            {result && <QuizResult result={result} userAnswer={userAnswer} />}
          </>
        )}

        {!quiz && !error && !loading && !showingSummary && (
          <div className="text-center text-gray-400 mt-12">
            <p>No quiz loaded.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuizPage;
