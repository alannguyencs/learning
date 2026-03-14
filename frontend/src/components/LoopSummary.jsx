import React from "react";

const LoopSummary = ({
  loopProgress,
  onNextLoop,
  scope,
  topicName,
  lessonTitle,
}) => {
  const { correct, incorrect, total } = loopProgress;
  const accuracy = total > 0 ? Math.round((correct / total) * 100) : 0;
  const correctPct = total > 0 ? (correct / total) * 100 : 0;

  const hasLesson = scope?.lessonId != null;
  const hasTopic = scope?.topicId != null;

  return (
    <div className="bg-gray-700 rounded-lg p-6 border border-gray-600 text-center">
      <h2 className="text-xl text-white font-semibold mb-2">Loop Complete</h2>
      <p className="text-gray-400 text-sm mb-6">
        You answered all {total} questions
      </p>

      <div className="flex justify-center gap-8 mb-6">
        <div>
          <span className="text-3xl font-bold text-green-400">{correct}</span>
          <p className="text-sm text-gray-400 mt-1">Correct</p>
        </div>
        <div>
          <span className="text-3xl font-bold text-red-400">{incorrect}</span>
          <p className="text-sm text-gray-400 mt-1">Incorrect</p>
        </div>
        <div>
          <span className="text-3xl font-bold text-blue-400">{accuracy}%</span>
          <p className="text-sm text-gray-400 mt-1">Accuracy</p>
        </div>
      </div>

      <div className="w-full h-3 bg-gray-600 rounded-full overflow-hidden mb-6">
        <div
          className="h-full bg-green-500 rounded-full transition-all"
          style={{ width: `${correctPct}%` }}
        />
      </div>

      <div className="flex flex-col gap-3">
        {hasLesson && (
          <button
            onClick={() =>
              onNextLoop({ topicId: scope.topicId, lessonId: scope.lessonId })
            }
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded transition-colors"
          >
            Next Loop - {lessonTitle || "This Lesson"}
          </button>
        )}

        {hasTopic && (
          <button
            onClick={() =>
              onNextLoop({ topicId: scope.topicId, lessonId: null })
            }
            className={`w-full font-bold py-2 px-6 rounded transition-colors ${
              hasLesson
                ? "border border-gray-500 text-gray-300 hover:bg-gray-600 hover:text-white"
                : "bg-blue-600 hover:bg-blue-700 text-white"
            }`}
          >
            Next Loop - {topicName || "This Topic"}
          </button>
        )}

        <button
          onClick={() => onNextLoop({ topicId: null, lessonId: null })}
          className={`w-full font-bold py-2 px-6 rounded transition-colors ${
            hasTopic
              ? "border border-gray-500 text-gray-300 hover:bg-gray-600 hover:text-white"
              : "bg-blue-600 hover:bg-blue-700 text-white"
          }`}
        >
          {hasTopic ? "Next Loop - All Topics" : "Next Loop"}
        </button>
      </div>
    </div>
  );
};

export default LoopSummary;
