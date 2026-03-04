"""CRUD operations for QuizQuestion — pre-generated question bank."""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.quiz_question import QuizQuestion

logger = logging.getLogger(__name__)


def get_question(
    db: Session,
    lesson_id: int,
    quiz_type: str,
    exclude_ids: Optional[List[int]] = None,
) -> Optional[QuizQuestion]:
    """Select a question from the bank, excluding already-seen IDs."""
    query = db.query(QuizQuestion).filter(
        QuizQuestion.lesson_id == lesson_id,
        QuizQuestion.quiz_type == quiz_type,
    )
    if exclude_ids:
        query = query.filter(QuizQuestion.id.notin_(exclude_ids))
    return query.order_by(QuizQuestion.id).first()


def get_question_by_id(db: Session, question_id: int) -> Optional[QuizQuestion]:
    """Get a question by its ID."""
    return db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()


def get_question_count(db: Session, lesson_id: int) -> int:
    """Count available questions for a lesson."""
    return db.query(QuizQuestion).filter(QuizQuestion.lesson_id == lesson_id).count()


def get_question_count_for_topic(db: Session, topic_id: str) -> int:
    """Count available questions for a topic."""
    return db.query(QuizQuestion).filter(QuizQuestion.topic_id == topic_id).count()


def get_total_question_count(db: Session) -> int:
    """Count all questions in the bank."""
    return db.query(QuizQuestion).count()


def create_quiz_questions(db: Session, questions: list[dict]) -> int:
    """Bulk insert quiz questions and return the count inserted."""
    objects = [QuizQuestion(**q) for q in questions]
    db.add_all(objects)
    db.commit()
    return len(objects)
