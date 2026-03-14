"""Lesson schemas for request/response models."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class LessonCreate(BaseModel):
    """Request body for creating a lesson."""

    topic: str
    topic_name: Optional[str] = None
    title: str
    published_date: Optional[date] = None
    content: Optional[str] = None


class LessonResponse(BaseModel):
    """Response for lesson list items (no content)."""

    id: int
    topic: str
    topic_name: Optional[str] = None
    title: str
    published_date: Optional[date] = None
    created_at: datetime


class LessonDetailResponse(LessonResponse):
    """Response for single lesson (includes content)."""

    content: Optional[str] = None


class LessonUpdate(BaseModel):
    """Request body for updating a lesson."""

    title: Optional[str] = None
    published_date: Optional[date] = None
    content: Optional[str] = None
