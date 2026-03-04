import React, { useState, useEffect } from "react";
import apiService from "../services/api";

const TopicLessonFilter = ({ scope, onScopeChange }) => {
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState("");
  const [selectedLesson, setSelectedLesson] = useState("");

  useEffect(() => {
    const loadTopics = async () => {
      try {
        const data = await apiService.getQuizTopics();
        setTopics(data.topics || []);
      } catch {
        setTopics([]);
      }
    };
    loadTopics();
  }, []);

  const handleTopicChange = (e) => {
    const topicId = e.target.value;
    setSelectedTopic(topicId);
    setSelectedLesson("");
    onScopeChange({
      topicId: topicId || null,
      lessonId: null,
    });
  };

  const handleLessonChange = (e) => {
    const lessonId = e.target.value;
    setSelectedLesson(lessonId);
    onScopeChange({
      topicId: selectedTopic || null,
      lessonId: lessonId ? parseInt(lessonId, 10) : null,
    });
  };

  const currentTopic = topics.find((t) => t.topic_id === selectedTopic);

  return (
    <div className="flex gap-4 items-center">
      <select
        value={selectedTopic}
        onChange={handleTopicChange}
        className="bg-gray-700 text-gray-200 border border-gray-600 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">All Topics</option>
        {topics.map((topic) => (
          <option key={topic.topic_id} value={topic.topic_id}>
            {topic.topic_name}
          </option>
        ))}
      </select>

      {currentTopic && currentTopic.lessons.length > 0 && (
        <select
          value={selectedLesson}
          onChange={handleLessonChange}
          className="bg-gray-700 text-gray-200 border border-gray-600 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Lessons</option>
          {currentTopic.lessons.map((lesson) => (
            <option key={lesson.lesson_id} value={lesson.lesson_id}>
              {lesson.lesson_name}
            </option>
          ))}
        </select>
      )}
    </div>
  );
};

export default TopicLessonFilter;
