"""CRUD operations for UserLessonMemory — lesson-level MEMORIZE state."""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.user_lesson_memory import UserLessonMemory

logger = logging.getLogger(__name__)

DEFAULT_N_INITIAL = 0.3
ALPHA = 0.3
BETA = 0.2


def get_or_create_memory(
    db: Session, username: str, topic_id: str, lesson_id: int
) -> UserLessonMemory:
    """Get or lazily create a lesson memory record."""
    record = (
        db.query(UserLessonMemory)
        .filter(
            UserLessonMemory.username == username,
            UserLessonMemory.lesson_id == lesson_id,
        )
        .first()
    )
    if record:
        return record

    record = UserLessonMemory(
        username=username,
        topic_id=topic_id,
        lesson_id=lesson_id,
        forgetting_rate=DEFAULT_N_INITIAL,
        last_review_at=None,
        last_review_quiz_count=None,
        review_count=0,
        correct_count=0,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_memory_on_quiz_result(
    db: Session,
    username: str,
    lesson_id: int,
    is_correct: bool,
    current_quiz_count: int,
) -> Optional[UserLessonMemory]:
    """Update lesson memory after a quiz result."""
    record = (
        db.query(UserLessonMemory)
        .filter(
            UserLessonMemory.username == username,
            UserLessonMemory.lesson_id == lesson_id,
        )
        .first()
    )
    if not record:
        return None

    if is_correct:
        record.update_on_correct(ALPHA)
        record.correct_count += 1
    else:
        record.update_on_incorrect(BETA)

    record.review_count += 1
    record.last_review_at = datetime.utcnow()
    record.last_review_quiz_count = current_quiz_count

    db.commit()
    db.refresh(record)
    return record


def get_lesson_memories_for_topic(
    db: Session, username: str, topic_id: str
) -> List[UserLessonMemory]:
    """All lesson memories for a specific topic."""
    return (
        db.query(UserLessonMemory)
        .filter(
            UserLessonMemory.username == username,
            UserLessonMemory.topic_id == topic_id,
        )
        .all()
    )


def get_all_lesson_memories(db: Session, username: str) -> List[UserLessonMemory]:
    """All lesson memories for a user."""
    return db.query(UserLessonMemory).filter(UserLessonMemory.username == username).all()
