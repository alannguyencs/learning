import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import apiService from "../services/api";
import MarkdownPreview from "../components/MarkdownPreview";

const LessonDetailPage = () => {
  const { lessonId } = useParams();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLesson = async () => {
      try {
        const data = await apiService.getLessonById(lessonId);
        setLesson(data);
      } catch (err) {
        setError(
          err.response?.status === 404
            ? "Lesson not found"
            : "Failed to load lesson",
        );
      } finally {
        setLoading(false);
      }
    };
    fetchLesson();
  }, [lessonId]);

  return (
    <div className="min-h-screen bg-gray-800 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6 flex items-center justify-between">
          <button
            onClick={() => navigate("/dashboard")}
            className="text-gray-400 hover:text-white transition-colors text-sm"
          >
            &larr; Back to Lessons
          </button>
          {lesson && (
            <button
              onClick={() => navigate(`/quiz?lessonId=${lessonId}`)}
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded transition-colors text-sm"
            >
              Take Quiz
            </button>
          )}
        </div>

        {loading && (
          <div className="text-center text-gray-400 py-12">
            Loading lesson...
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-500/20 text-red-400 rounded-lg border border-red-500/30">
            {error}
          </div>
        )}

        {!loading && lesson && (
          <>
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-white mb-3">
                {lesson.title}
              </h1>
              <div className="flex items-center gap-4 text-sm text-gray-400">
                <span>{lesson.topic_name || lesson.topic}</span>
                {lesson.published_date && (
                  <>
                    <span>|</span>
                    <span>{lesson.published_date}</span>
                  </>
                )}
              </div>
            </div>

            <div className="bg-gray-700 rounded-lg p-6 border border-gray-600">
              <MarkdownPreview content={lesson.content} />
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default LessonDetailPage;
