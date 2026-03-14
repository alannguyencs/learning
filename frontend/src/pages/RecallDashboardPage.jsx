import React from "react";
import { useNavigate } from "react-router-dom";
import useDashboardData from "../hooks/useDashboardData";
import RecallSummary from "../components/RecallSummary";
import RecallHeatmap from "../components/RecallHeatmap";
import TopicMatrix from "../components/TopicMatrix";

const RecallDashboardPage = () => {
  const navigate = useNavigate();
  const {
    loading,
    error,
    recallMap,
    topicMatrix,
    expandedTopics,
    toggleTopic,
  } = useDashboardData();

  return (
    <div className="min-h-screen bg-gray-800 p-8">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold text-white">Recall Dashboard</h1>
          <div className="flex gap-3">
            <button
              onClick={() => navigate("/dashboard")}
              className="px-4 py-2 rounded border border-gray-500 text-gray-300 hover:bg-gray-600 hover:text-white transition-colors text-sm font-medium"
            >
              Lessons
            </button>
            <button
              onClick={() => navigate("/quiz")}
              className="px-4 py-2 rounded border border-gray-500 text-gray-300 hover:bg-gray-600 hover:text-white transition-colors text-sm font-medium"
            >
              Quiz
            </button>
          </div>
        </div>

        {loading && (
          <div className="text-center text-gray-400 py-12">
            Loading dashboard...
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-500/20 text-red-400 rounded-lg border border-red-500/30">
            {error}
          </div>
        )}

        {!loading && recallMap && (
          <div className="space-y-8">
            <section>
              <h2 className="text-lg font-semibold text-gray-300 mb-4">
                Summary
              </h2>
              <RecallSummary
                globalRecall={recallMap.global_recall}
                globalAccuracy={recallMap.global_accuracy}
                topicsAtRisk={recallMap.topics_at_risk}
                lessonsAtRisk={recallMap.lessons_at_risk}
              />
            </section>

            <section>
              <h2 className="text-lg font-semibold text-gray-300 mb-4">
                Topic Recall
              </h2>
              <RecallHeatmap
                topics={recallMap.topics}
                expandedTopics={expandedTopics}
                onToggleTopic={toggleTopic}
              />
            </section>

            {topicMatrix && (
              <section>
                <h2 className="text-lg font-semibold text-gray-300 mb-4">
                  Quiz History
                </h2>
                <div className="bg-gray-700 rounded-lg p-4 border border-gray-600">
                  <TopicMatrix
                    topics={topicMatrix.topics}
                    maxQuizCount={topicMatrix.max_quiz_count}
                  />
                </div>
              </section>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default RecallDashboardPage;
