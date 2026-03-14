"""Pydantic schemas for recall dashboard endpoints."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class LessonRecallItem(BaseModel):
    """Per-lesson recall data nested within a topic."""

    lesson_id: int
    lesson_name: str
    recall_probability: float
    forgetting_rate: float
    last_review_at: Optional[datetime]
    review_count: int
    correct_count: int


class TopicRecallItem(BaseModel):
    """Per-topic recall data with nested lessons."""

    topic_id: str
    topic_name: str
    lesson_count: int
    recall_probability: float
    forgetting_rate: float
    last_review_at: Optional[datetime]
    review_count: int
    correct_count: int
    lessons: List[LessonRecallItem]


class RecallMapResponse(BaseModel):
    """Full recall map with summary stats."""

    topics: List[TopicRecallItem]
    global_recall: float
    global_accuracy: float
    topics_at_risk: int
    lessons_at_risk: int


class TopicQuizAttempt(BaseModel):
    """Single quiz attempt cell in the topic matrix."""

    quiz_id: int
    result: Optional[str]
    asked_at: Optional[datetime]
    column_index: int
    lesson_name: str


class TopicMatrixRow(BaseModel):
    """One row in the topic matrix grid."""

    topic_id: str
    topic_name: str
    lesson_count: int
    last_quiz_at: Optional[datetime]
    quizzes: List[TopicQuizAttempt]


class TopicMatrixResponse(BaseModel):
    """Full topic matrix response."""

    topics: List[TopicMatrixRow]
    max_quiz_count: int
