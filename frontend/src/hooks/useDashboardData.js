import { useState, useEffect, useCallback } from "react";
import apiService from "../services/api";

const useDashboardData = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recallMap, setRecallMap] = useState(null);
  const [topicMatrix, setTopicMatrix] = useState(null);
  const [expandedTopics, setExpandedTopics] = useState(new Set());

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [mapData, matrixData] = await Promise.all([
        apiService.getRecallMap(),
        apiService.getTopicMatrix(),
      ]);
      setRecallMap(mapData);
      setTopicMatrix(matrixData);
    } catch (err) {
      setError("Failed to load dashboard data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const toggleTopic = useCallback((topicId) => {
    setExpandedTopics((prev) => {
      const next = new Set(prev);
      if (next.has(topicId)) {
        next.delete(topicId);
      } else {
        next.add(topicId);
      }
      return next;
    });
  }, []);

  return {
    loading,
    error,
    recallMap,
    topicMatrix,
    expandedTopics,
    toggleTopic,
    refresh: fetchData,
  };
};

export default useDashboardData;
