"""CRUD operations for Lesson — normalized lesson records."""

import logging
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from src.models.lesson import Lesson

logger = logging.getLogger(__name__)


def create_lesson(
    db: Session,
    topic: str,
    title: str,
    published_date: Optional[date] = None,
    content: Optional[str] = None,
    topic_name: Optional[str] = None,
) -> Lesson:
    """Insert a new lesson and return the created record."""
    lesson = Lesson(
        topic=topic,
        topic_name=topic_name,
        title=title,
        published_date=published_date,
        content=content,
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


def get_lesson_by_id(db: Session, lesson_id: int) -> Optional[Lesson]:
    """Select a lesson by primary key."""
    return db.query(Lesson).filter(Lesson.id == lesson_id).first()


def get_lessons_by_topic(db: Session, topic: str) -> list[Lesson]:
    """Select all lessons for a topic."""
    return (
        db.query(Lesson)
        .filter(Lesson.topic == topic)
        .order_by(Lesson.id)
        .all()
    )


def get_all_lessons(db: Session) -> list[Lesson]:
    """Select all lessons ordered by topic, id."""
    return db.query(Lesson).order_by(Lesson.topic, Lesson.id).all()


def update_lesson(db: Session, lesson_id: int, **fields) -> Optional[Lesson]:
    """Update mutable fields on a lesson. Returns updated record or None."""
    lesson = get_lesson_by_id(db, lesson_id)
    if not lesson:
        return None

    allowed = {"title", "published_date", "content"}
    for key, value in fields.items():
        if key in allowed and value is not None:
            setattr(lesson, key, value)

    db.commit()
    db.refresh(lesson)
    return lesson
