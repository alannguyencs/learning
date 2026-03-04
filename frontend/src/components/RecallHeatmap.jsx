import React from "react";
import LessonRecallList from "./LessonRecallList";
import QuizLaunchButton from "./QuizLaunchButton";

const cardBorder = (recall) => {
  if (recall >= 0.7) return "border-green-500/40";
  if (recall >= 0.5) return "border-yellow-500/40";
  return "border-red-500/40";
};

const cardBg = (recall) => {
  if (recall >= 0.7) return "bg-green-500/5";
  if (recall >= 0.5) return "bg-yellow-500/5";
  return "bg-red-500/5";
};

const recallColor = (recall) => {
  if (recall >= 0.7) return "text-green-400";
  if (recall >= 0.5) return "text-yellow-400";
  return "text-red-400";
};

const RecallHeatmap = ({ topics, expandedTopics, onToggleTopic }) => {
  if (!topics || topics.length === 0) {
    return <p className="text-gray-400">No topic data available.</p>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {topics.map((topic) => {
        const isExpanded = expandedTopics.has(topic.topic_id);
        const accuracy =
          topic.review_count > 0
            ? Math.round((topic.correct_count / topic.review_count) * 100)
            : 0;

        return (
          <div
            key={topic.topic_id}
            className={`rounded-lg border p-4 transition-colors ${cardBorder(topic.recall_probability)} ${cardBg(topic.recall_probability)}`}
          >
            <div
              className="flex items-center justify-between cursor-pointer"
              onClick={() => onToggleTopic(topic.topic_id)}
            >
              <div className="flex-1 min-w-0 mr-3">
                <h3 className="text-white font-semibold truncate">
                  {topic.topic_name}
                </h3>
                <div className="flex gap-3 mt-1 text-xs text-gray-400">
                  <span>{topic.lesson_count} lessons</span>
                  <span>{topic.review_count} reviews</span>
                  <span>{accuracy}% accuracy</span>
                </div>
              </div>
              <div className="flex items-center gap-3 shrink-0">
                <span
                  className={`text-xl font-bold ${recallColor(topic.recall_probability)}`}
                >
                  {Math.round(topic.recall_probability * 100)}%
                </span>
                <QuizLaunchButton topicId={topic.topic_id} />
                <span className="text-gray-400 text-sm">
                  {isExpanded ? "\u25B2" : "\u25BC"}
                </span>
              </div>
            </div>

            {isExpanded && (
              <LessonRecallList
                lessons={topic.lessons}
                topicId={topic.topic_id}
              />
            )}
          </div>
        );
      })}
    </div>
  );
};

export default RecallHeatmap;
