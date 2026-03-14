import React from "react";

const LoopSummary = ({ loopProgress, onNextLoop }) => {
  const { correct, incorrect, loopNumber, total } = loopProgress;
  const accuracy = total > 0 ? Math.round((correct / total) * 100) : 0;
  const correctPct = total > 0 ? (correct / total) * 100 : 0;

  return (
    <div className="bg-gray-700 rounded-lg p-6 border border-gray-600 text-center">
      <h2 className="text-xl text-white font-semibold mb-2">
        Loop {loopNumber} Complete
      </h2>
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

      <button
        onClick={onNextLoop}
        className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded transition-colors"
      >
        Next Loop
      </button>
    </div>
  );
};

export default LoopSummary;
