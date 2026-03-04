import React from "react";
import { useNavigate } from "react-router-dom";
import useQuiz from "../hooks/useQuiz";
import TopicLessonFilter from "../components/TopicLessonFilter";
import QuizCard from "../components/QuizCard";
import QuizResult from "../components/QuizResult";

const QuizPage = () => {
  const navigate = useNavigate();
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
    reset,
  } = useQuiz();

  const handleScopeChange = (newScope) => {
    setScope(newScope);
    reset();
  };

  return (
    <div className="min-h-screen bg-gray-800 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="mb-6 flex items-center justify-between gap-4 flex-wrap">
          <TopicLessonFilter scope={scope} onScopeChange={handleScopeChange} />
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate("/dashboard")}
              className="px-4 py-2 rounded border border-gray-500 text-gray-300 hover:bg-gray-600 hover:text-white transition-colors text-sm font-medium"
            >
              Dashboard
            </button>
            <button
              onClick={fetchNextQuiz}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Loading..." : "Next Quiz"}
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/20 text-red-400 rounded-lg border border-red-500/30">
            {error}
          </div>
        )}

        {quiz && (
          <QuizCard quiz={quiz} onSubmit={submitAnswer} disabled={loading || !!result} result={result} userAnswer={userAnswer} />
        )}

        {result && <QuizResult result={result} userAnswer={userAnswer} />}

        {!quiz && !error && !loading && (
          <div className="text-center text-gray-400 mt-12">
            <p>Select a scope and click "Next Quiz" to begin.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuizPage;
