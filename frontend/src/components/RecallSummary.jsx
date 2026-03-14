import React from "react";

const SummaryCard = ({ label, value, color }) => (
  <div className="bg-gray-700 rounded-lg p-4 border border-gray-600 flex-1 min-w-[140px]">
    <div className="text-sm text-gray-400 mb-1">{label}</div>
    <div className={`text-2xl font-bold ${color}`}>{value}</div>
  </div>
);

const pctColor = (value) =>
  value >= 0.7
    ? "text-green-400"
    : value >= 0.5
      ? "text-yellow-400"
      : "text-red-400";

const RecallSummary = ({
  globalRecall,
  globalAccuracy,
  topicsAtRisk,
  lessonsAtRisk,
}) => {
  return (
    <div className="flex gap-4 flex-wrap">
      <SummaryCard
        label="Global Recall"
        value={`${Math.round(globalRecall * 100)}%`}
        color={pctColor(globalRecall)}
      />
      <SummaryCard
        label="Quiz Accuracy"
        value={`${Math.round(globalAccuracy * 100)}%`}
        color={pctColor(globalAccuracy)}
      />
      <SummaryCard
        label="Topics at Risk"
        value={topicsAtRisk}
        color={topicsAtRisk > 0 ? "text-red-400" : "text-green-400"}
      />
      <SummaryCard
        label="Lessons at Risk"
        value={lessonsAtRisk}
        color={lessonsAtRisk > 0 ? "text-red-400" : "text-green-400"}
      />
    </div>
  );
};

export default RecallSummary;
