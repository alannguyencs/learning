import React, { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import apiService from "../services/api";

const recallColor = (value) => {
  if (value === null) return "text-gray-500";
  if (value >= 0.7) return "text-green-400";
  if (value >= 0.4) return "text-yellow-400";
  return "text-red-400";
};

const LessonDashboardPage = () => {
  const navigate = useNavigate();
  const [lessons, setLessons] = useState([]);
  const [recallMap, setRecallMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [topicFilter, setTopicFilter] = useState("");
  const [sortKey, setSortKey] = useState("published_date");
  const [sortDir, setSortDir] = useState("desc");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [lessonData, recallData] = await Promise.all([
          apiService.getLessons(),
          apiService.getRecallMap().catch(() => null),
        ]);
        setLessons(lessonData.lessons || []);

        if (recallData?.topics) {
          const map = {};
          for (const topic of recallData.topics) {
            for (const lesson of topic.lessons || []) {
              map[lesson.lesson_id] = {
                recall: lesson.recall_probability,
                reviewed: lesson.last_review_at !== null,
                accuracy:
                  lesson.last_review_at !== null && lesson.review_count > 0
                    ? lesson.correct_count / lesson.review_count
                    : null,
              };
            }
          }
          setRecallMap(map);
        }
      } catch {
        setError("Failed to load lessons");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const topicDisplay = (lesson) => lesson.topic_name || lesson.topic;

  const topics = useMemo(
    () =>
      [...new Map(lessons.map((l) => [l.topic, topicDisplay(l)])).entries()]
        .sort((a, b) => a[1].localeCompare(b[1]))
        .map(([id, name]) => ({ id, name })),
    [lessons],
  );

  const getRecall = useMemo(
    () => (lessonId) => {
      const entry = recallMap[lessonId];
      if (!entry || !entry.reviewed) return null;
      return entry.recall;
    },
    [recallMap],
  );

  const getAccuracy = useMemo(
    () => (lessonId) => {
      const entry = recallMap[lessonId];
      if (!entry) return null;
      return entry.accuracy;
    },
    [recallMap],
  );

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir(key === "published_date" ? "desc" : "asc");
    }
  };

  const sortIndicator = (key) => {
    if (sortKey !== key) return "";
    return sortDir === "asc" ? " \u25B2" : " \u25BC";
  };

  const filtered = useMemo(() => {
    let result = lessons;
    if (topicFilter) {
      result = result.filter((l) => l.topic === topicFilter);
    }
    if (!sortKey) return result;

    return [...result].sort((a, b) => {
      let aVal, bVal;
      if (sortKey === "topic") {
        aVal = topicDisplay(a).toLowerCase();
        bVal = topicDisplay(b).toLowerCase();
      } else if (sortKey === "recall") {
        aVal = getRecall(a.id) ?? -1;
        bVal = getRecall(b.id) ?? -1;
      } else if (sortKey === "accuracy") {
        aVal = getAccuracy(a.id) ?? -1;
        bVal = getAccuracy(b.id) ?? -1;
      } else {
        aVal = (a[sortKey] || "").toLowerCase();
        bVal = (b[sortKey] || "").toLowerCase();
      }
      if (aVal < bVal) return sortDir === "asc" ? -1 : 1;
      if (aVal > bVal) return sortDir === "asc" ? 1 : -1;
      return 0;
    });
  }, [lessons, topicFilter, sortKey, sortDir, getRecall, getAccuracy]);

  const thClass =
    "px-4 py-3 cursor-pointer select-none hover:text-white transition-colors";

  return (
    <div className="min-h-screen bg-gray-800 p-8">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold text-white">Lessons</h1>
          <div className="flex gap-3">
            <button
              onClick={() => navigate("/quiz")}
              className="px-4 py-2 rounded border border-gray-500 text-gray-300 hover:bg-gray-600 hover:text-white transition-colors text-sm font-medium"
            >
              Go to Quiz
            </button>
            <button
              onClick={() => navigate("/recall")}
              className="px-4 py-2 rounded border border-gray-500 text-gray-300 hover:bg-gray-600 hover:text-white transition-colors text-sm font-medium"
            >
              Recall Dashboard
            </button>
          </div>
        </div>

        <div className="flex items-center gap-4 mb-6">
          <select
            value={topicFilter}
            onChange={(e) => setTopicFilter(e.target.value)}
            className="bg-gray-700 text-gray-200 border border-gray-600 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            <option value="">All Topics</option>
            {topics.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </div>

        {loading && (
          <div className="text-center text-gray-400 py-12">
            Loading lessons...
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-500/20 text-red-400 rounded-lg border border-red-500/30">
            {error}
          </div>
        )}

        {!loading && lessons.length === 0 && !error && (
          <div className="text-center text-gray-400 py-12">
            No lessons found. Create lessons via the API to get started.
          </div>
        )}

        {!loading && filtered.length > 0 && (
          <div className="overflow-x-auto rounded-lg border border-gray-600">
            <table className="w-full text-left">
              <thead className="bg-gray-700 text-gray-300 text-sm uppercase tracking-wide">
                <tr>
                  <th className="px-4 py-3">Title</th>
                  <th className={`${thClass} w-48`} onClick={() => handleSort("topic")}>
                    Topic{sortIndicator("topic")}
                  </th>
                  <th
                    className={`${thClass} w-24 text-center`}
                    onClick={() => handleSort("recall")}
                  >
                    Recall{sortIndicator("recall")}
                  </th>
                  <th
                    className={`${thClass} w-24 text-center`}
                    onClick={() => handleSort("accuracy")}
                  >
                    Accuracy{sortIndicator("accuracy")}
                  </th>
                  <th className={`${thClass} w-36`} onClick={() => handleSort("published_date")}>
                    Published{sortIndicator("published_date")}
                  </th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((lesson) => {
                  const recall = getRecall(lesson.id);
                  const accuracy = getAccuracy(lesson.id);
                  return (
                    <tr
                      key={lesson.id}
                      onClick={() => navigate(`/lessons/${lesson.id}`)}
                      className="border-t border-gray-600 bg-gray-800 hover:bg-gray-700 cursor-pointer transition-colors"
                    >
                      <td className="px-4 py-3 text-white font-medium">
                        {lesson.title}
                      </td>
                      <td className="px-4 py-3 text-gray-400">
                        {topicDisplay(lesson)}
                      </td>
                      <td
                        className={`px-4 py-3 text-sm text-center font-medium ${recallColor(recall)}`}
                      >
                        {recall !== null
                          ? `${Math.round(recall * 100)}%`
                          : "-"}
                      </td>
                      <td
                        className={`px-4 py-3 text-sm text-center font-medium ${recallColor(accuracy)}`}
                      >
                        {accuracy !== null
                          ? `${Math.round(accuracy * 100)}%`
                          : "-"}
                      </td>
                      <td className="px-4 py-3 text-gray-400 text-sm">
                        {lesson.published_date || "-"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default LessonDashboardPage;
