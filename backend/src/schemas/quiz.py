"""Quiz schemas for request/response models."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class QuizNextResponse(BaseModel):
    """Response for GET /api/quiz/next."""

    quiz_id: int
    question: str
    options: Dict[str, str]
    quiz_type: str
    topic_id: str
    lesson_id: int
    correct_option_count: int


class QuizAnswerRequest(BaseModel):
    """Request body for POST /api/quiz/{quiz_id}/answer."""

    answer: List[str] = Field(..., min_length=1)


class QuizAnswerResponse(BaseModel):
    """Response for POST /api/quiz/{quiz_id}/answer."""

    is_correct: bool
    correct_options: List[str]
    quiz_learnt: str
    explanations: Dict[str, str]
    quiz_take_away: str


class QuizHistoryItem(BaseModel):
    """Single item in quiz history list."""

    quiz_id: int
    topic_id: str
    lesson_id: int
    quiz_type: str
    question: str
    user_answer: Optional[List[str]] = None
    assessment_result: Optional[str] = None
    created_at: datetime


class QuizStatsResponse(BaseModel):
    """Response for GET /api/quiz/stats."""

    total: int
    correct: int
    accuracy: float


class QuizEligibilityResponse(BaseModel):
    """Response for GET /api/quiz/eligibility."""

    eligible: bool
    reason: str


class LessonItem(BaseModel):
    """Single lesson in topic list."""

    lesson_id: int
    lesson_name: str


class TopicWithLessons(BaseModel):
    """Topic with nested lessons for scope filter."""

    topic_id: str
    topic_name: str
    lessons: List[LessonItem]
