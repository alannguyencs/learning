import axios from "axios";

export const API_BASE_URL = process.env.REACT_APP_API_URL || "";

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

const apiService = {
  login: async (username, password) => {
    const response = await api.post("/api/login/", { username, password });
    return response.data;
  },

  logout: async () => {
    const response = await api.post("/api/login/logout");
    return response.data;
  },

  getCurrentUser: async () => {
    try {
      const response = await api.get("/api/me");
      return response.data;
    } catch (error) {
      if (error.response?.status === 401) {
        return { authenticated: false };
      }
      throw error;
    }
  },

  getNextQuiz: async (topicId, lessonId) => {
    const params = new URLSearchParams();
    if (topicId) params.append("topic_id", topicId);
    if (lessonId) params.append("lesson_id", lessonId);
    const query = params.toString() ? `?${params}` : "";
    const response = await api.get(`/api/quiz/next${query}`);
    return response.data;
  },

  submitAnswer: async (quizId, answer) => {
    const response = await api.post(`/api/quiz/${quizId}/answer`, { answer });
    return response.data;
  },

  getQuizHistory: async (limit = 20, offset = 0) => {
    const response = await api.get(
      `/api/quiz/history?limit=${limit}&offset=${offset}`,
    );
    return response.data;
  },

  getQuizStats: async () => {
    const response = await api.get("/api/quiz/stats");
    return response.data;
  },

  getQuizTopics: async () => {
    const response = await api.get("/api/quiz/topics");
    return response.data;
  },

  getQuizEligibility: async () => {
    const response = await api.get("/api/quiz/eligibility");
    return response.data;
  },

  getRecallMap: async () => {
    const response = await api.get("/api/quiz/recall-map");
    return response.data;
  },

  getTopicMatrix: async () => {
    const response = await api.get("/api/quiz/topic-matrix");
    return response.data;
  },
};

export default apiService;
