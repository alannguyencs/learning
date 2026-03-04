import React from "react";
import QuizLaunchButton from "./QuizLaunchButton";

const recallColor = (recall) => {
  if (recall >= 0.7) return "text-green-400";
  if (recall >= 0.5) return "text-yellow-400";
  return "text-red-400";
};

const recallBg = (recall) => {
  if (recall >= 0.7) return "bg-green-500/10";
  if (recall >= 0.5) return "bg-yellow-500/10";
  return "bg-red-500/10";
};

const LessonRecallList = ({ lessons, topicId }) => {
  if (!lessons || lessons.length === 0) {
    return (
      <p className="text-gray-500 text-sm py-2">No lessons in this topic.</p>
    );
  }

  return (
    <div className="mt-2 space-y-1">
      {lessons.map((lesson) => {
        const accuracy =
          lesson.review_count > 0
            ? Math.round((lesson.correct_count / lesson.review_count) * 100)
            : 0;

        return (
          <div
            key={lesson.lesson_id}
            className={`flex items-center justify-between px-3 py-2 rounded ${recallBg(lesson.recall_probability)}`}
          >
            <div className="flex-1 min-w-0 mr-3">
              <span className="text-sm text-gray-200 truncate block">
                {lesson.lesson_name}
              </span>
            </div>
            <div className="flex items-center gap-4 shrink-0">
              <span
                className={`text-sm font-semibold ${recallColor(lesson.recall_probability)}`}
              >
                {Math.round(lesson.recall_probability * 100)}%
              </span>
              <span className="text-xs text-gray-400">
                {lesson.review_count} reviews
              </span>
              <span className="text-xs text-gray-400">{accuracy}% acc</span>
              <QuizLaunchButton topicId={topicId} lessonId={lesson.lesson_id} />
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default LessonRecallList;
