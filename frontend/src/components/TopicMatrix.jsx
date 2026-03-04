import React from "react";

const cellColor = (result) => {
  if (result === "correct") return "bg-green-500";
  if (result === "incorrect") return "bg-red-500";
  return "bg-gray-600";
};

const TopicMatrix = ({ topics, maxQuizCount }) => {
  if (!topics || topics.length === 0) {
    return <p className="text-gray-400">No quiz history yet.</p>;
  }

  // Only show topics that have quizzes
  const topicsWithQuizzes = topics.filter((t) => t.quizzes.length > 0);

  if (topicsWithQuizzes.length === 0) {
    return <p className="text-gray-400">No quiz history yet.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <div className="min-w-[400px]">
        {topicsWithQuizzes.map((topic) => (
          <div key={topic.topic_id} className="flex items-center mb-2">
            <div className="w-40 shrink-0 pr-3">
              <span className="text-sm text-gray-200 truncate block">
                {topic.topic_name}
              </span>
              <span className="text-xs text-gray-500">
                {topic.lesson_count} lessons
              </span>
            </div>
            <div className="flex gap-1 flex-wrap">
              {topic.quizzes.map((quiz) => (
                <div
                  key={quiz.quiz_id}
                  className={`w-4 h-4 rounded-sm ${cellColor(quiz.result)} cursor-default`}
                  title={`${quiz.lesson_name}\n${quiz.result || "pending"}\n${quiz.asked_at ? new Date(quiz.asked_at).toLocaleDateString() : ""}`}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopicMatrix;
