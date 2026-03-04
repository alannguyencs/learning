import React, { useState } from "react";

const OPTION_LABELS = ["A", "B", "C", "D"];

const QuizCard = ({ quiz, onSubmit, disabled, result = null, userAnswer = [] }) => {
  const [selected, setSelected] = useState([]);
  const isMulti = quiz.correct_option_count > 1;
  const answered = !!result;
  const correctOptions = result?.correct_options || [];

  const handleOptionClick = (label) => {
    if (disabled) return;

    if (isMulti) {
      setSelected((prev) =>
        prev.includes(label)
          ? prev.filter((l) => l !== label)
          : [...prev, label],
      );
    } else {
      onSubmit([label]);
    }
  };

  const handleMultiSubmit = () => {
    if (selected.length > 0) {
      onSubmit(selected);
    }
  };

  const getOptionStyle = (label) => {
    if (!answered) {
      const isSelected = selected.includes(label);
      if (isSelected) return "border-blue-500 bg-blue-500/20 text-white";
      return "border-gray-600 bg-gray-800 text-gray-200 hover:border-gray-500";
    }

    const isCorrect = correctOptions.includes(label);
    const isUserPick = userAnswer.includes(label);

    if (isUserPick && !isCorrect) return "border-red-500 bg-red-500/20 text-red-300";
    if (isCorrect) return "border-green-500 bg-green-500/20 text-green-300";
    return "border-gray-600 bg-gray-800 text-gray-400";
  };

  return (
    <div className="bg-gray-700 rounded-lg p-6 border border-gray-600">
      <div className="mb-1 text-sm text-gray-400 uppercase tracking-wide">
        {quiz.quiz_type}
      </div>
      <h2 className="text-xl text-white font-semibold mb-6">
        {quiz.question}
      </h2>

      {isMulti && !answered && (
        <p className="text-sm text-blue-400 mb-4">Select all that apply</p>
      )}

      <div className="space-y-3">
        {OPTION_LABELS.map((label) => {
          const optionText = quiz.options[label];
          if (!optionText) return null;

          return (
            <button
              key={label}
              onClick={() => handleOptionClick(label)}
              disabled={disabled}
              className={`w-full text-left px-4 py-3 rounded border transition-colors ${getOptionStyle(label)} ${disabled ? "cursor-default" : "cursor-pointer"}`}
            >
              <span className="font-bold mr-3">{label}.</span>
              {optionText}
            </button>
          );
        })}
      </div>

      {isMulti && !answered && (
        <button
          onClick={handleMultiSubmit}
          disabled={disabled || selected.length === 0}
          className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Submit Answer
        </button>
      )}
    </div>
  );
};

export default QuizCard;
