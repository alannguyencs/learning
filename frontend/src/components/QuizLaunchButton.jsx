import React from "react";
import { useNavigate } from "react-router-dom";

const QuizLaunchButton = ({ topicId, lessonId, size = "sm" }) => {
  const navigate = useNavigate();

  const handleClick = (e) => {
    e.stopPropagation();
    const params = new URLSearchParams();
    if (topicId) params.append("topicId", topicId);
    if (lessonId) params.append("lessonId", lessonId);
    navigate(`/quiz?${params}`);
  };

  const sizeClasses =
    size === "sm" ? "px-2 py-1 text-xs" : "px-3 py-1.5 text-sm";

  return (
    <button
      onClick={handleClick}
      className={`${sizeClasses} bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors font-medium`}
    >
      Quiz
    </button>
  );
};

export default QuizLaunchButton;
