"""API routes for lesson management."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.auth import authenticate_user_from_request
from src.crud.crud_lesson import (
    create_lesson,
    get_all_lessons,
    get_lesson_by_id,
    get_lessons_by_topic,
    update_lesson,
)
from src.database import get_db
from src.schemas.lesson import (
    LessonCreate,
    LessonDetailResponse,
    LessonResponse,
    LessonUpdate,
)
from src.service.topic_lookup import register_topic

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lessons", tags=["lessons"])


def _get_user_or_401(request: Request, db: Session):
    """Authenticate user or raise 401."""
    user = authenticate_user_from_request(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user


@router.post("", response_model=LessonResponse, status_code=201)
async def create_lesson_endpoint(
    request: Request,
    body: LessonCreate,
    db: Session = Depends(get_db),
):
    """Create a new lesson."""
    _get_user_or_401(request, db)

    lesson = create_lesson(
        db,
        topic=body.topic,
        title=body.title,
        published_date=body.published_date,
        content=body.content,
        topic_name=body.topic_name,
    )

    # Register in topic_lookup cache
    register_topic(
        topic_id=lesson.topic,
        topic_name=body.topic_name or lesson.topic,
        lesson_id=lesson.id,
        lesson_name=lesson.title,
        lesson_filename="",
    )

    return LessonResponse(
        id=lesson.id,
        topic=lesson.topic,
        topic_name=lesson.topic_name,
        title=lesson.title,
        published_date=lesson.published_date,
        created_at=lesson.created_at,
    )


@router.get("", response_model=dict)
async def list_lessons(
    request: Request,
    db: Session = Depends(get_db),
    topic: Optional[str] = None,
):
    """List all lessons, optionally filtered by topic."""
    _get_user_or_401(request, db)

    if topic:
        lessons = get_lessons_by_topic(db, topic)
    else:
        lessons = get_all_lessons(db)

    return {
        "lessons": [
            LessonResponse(
                id=l.id,
                topic=l.topic,
                topic_name=l.topic_name,
                title=l.title,
                published_date=l.published_date,
                created_at=l.created_at,
            )
            for l in lessons
        ]
    }


@router.get("/{lesson_id}", response_model=LessonDetailResponse)
async def get_lesson(
    request: Request,
    lesson_id: int,
    db: Session = Depends(get_db),
):
    """Get a single lesson with content."""
    _get_user_or_401(request, db)

    lesson = get_lesson_by_id(db, lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )

    return LessonDetailResponse(
        id=lesson.id,
        topic=lesson.topic,
        topic_name=lesson.topic_name,
        title=lesson.title,
        published_date=lesson.published_date,
        content=lesson.content,
        created_at=lesson.created_at,
    )


@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson_endpoint(
    request: Request,
    lesson_id: int,
    body: LessonUpdate,
    db: Session = Depends(get_db),
):
    """Update a lesson's mutable fields."""
    _get_user_or_401(request, db)

    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    lesson = update_lesson(db, lesson_id, **updates)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )

    return LessonResponse(
        id=lesson.id,
        topic=lesson.topic,
        topic_name=lesson.topic_name,
        title=lesson.title,
        published_date=lesson.published_date,
        created_at=lesson.created_at,
    )
