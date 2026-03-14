"""CRUD operations for UserQuestionMemory — question-level MEMORIZE state."""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.user_question_memory import UserQuestionMemory

logger = logging.getLogger(__name__)

DEFAULT_N_INITIAL = 0.3
ALPHA = 0.3
BETA = 0.2


def get_or_create_memory(db: Session, username: str, quiz_question_id: int) -> UserQuestionMemory:
    """Get or lazily create a question memory record."""
    record = (
        db.query(UserQuestionMemory)
        .filter(
            UserQuestionMemory.username == username,
            UserQuestionMemory.quiz_question_id == quiz_question_id,
        )
        .first()
    )
    if record:
        return record

    record = UserQuestionMemory(
        username=username,
        quiz_question_id=quiz_question_id,
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


def get_question_memories_for_ids(
    db: Session, username: str, question_ids: List[int]
) -> List[UserQuestionMemory]:
    """Batch load question memories for a list of question IDs."""
    if not question_ids:
        return []
    return (
        db.query(UserQuestionMemory)
        .filter(
            UserQuestionMemory.username == username,
            UserQuestionMemory.quiz_question_id.in_(question_ids),
        )
        .all()
    )


def update_memory_on_quiz_result(
    db: Session,
    username: str,
    quiz_question_id: int,
    is_correct: bool,
    current_quiz_count: int,
) -> UserQuestionMemory:
    """Update question memory after a quiz result. Creates if needed."""
    record = get_or_create_memory(db, username, quiz_question_id)

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
