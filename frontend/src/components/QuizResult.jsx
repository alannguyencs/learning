import React from "react";

const QuizResult = ({ result, userAnswer = [] }) => {
  const isCorrect = result.is_correct;
  const correctOptions = result.correct_options || [];
  const wrongSelections = userAnswer.filter((a) => !correctOptions.includes(a));

  return (
    <div className="space-y-4 mt-4">
      {!isCorrect && result.explanations && (
        <div className="bg-gray-700 rounded-lg p-4 border border-red-500/30">
          <div className="space-y-2">
            {wrongSelections.map((label) => (
              <p key={label} className="text-lg text-gray-200">
                <span className="font-bold text-red-400 mr-1">{label}.</span>
                {result.explanations[label]}
              </p>
            ))}
          </div>
        </div>
      )}

      {result.explanations && (
        <div className="bg-gray-700 rounded-lg p-4 border border-green-500/30">
          <div className="space-y-2">
            {correctOptions.map((label) => (
              <p key={label} className="text-lg text-gray-200">
                <span className="font-bold text-green-400 mr-1">{label}.</span>
                {result.explanations[label]}
              </p>
            ))}
          </div>
        </div>
      )}

      {result.quiz_take_away && (
        <div className="bg-blue-500/10 rounded-lg p-4 border border-blue-500/30">
          <h3 className="text-sm font-semibold text-blue-400 uppercase mb-2">
            Key Takeaway
          </h3>
          <p className="text-lg text-gray-200">{result.quiz_take_away}</p>
        </div>
      )}
    </div>
  );
};

export default QuizResult;
