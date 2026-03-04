"""CRUD operations for QuizLog."""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.quiz_log import QuizLog

logger = logging.getLogger(__name__)


def create_quiz_log(
    db: Session,
    username: str,
    quiz_question_id: int,
    topic_id: str,
    lesson_id: int,
    quiz_type: str,
) -> QuizLog:
    """Insert a pending quiz log entry."""
    quiz_log = QuizLog(
        username=username,
        quiz_question_id=quiz_question_id,
        topic_id=topic_id,
        lesson_id=lesson_id,
        quiz_type=quiz_type,
    )
    db.add(quiz_log)
    db.commit()
    db.refresh(quiz_log)
    return quiz_log


def record_quiz_answer(
    db: Session,
    quiz_id: int,
    user_answer: List[str],
    assessment_result: str,
) -> Optional[QuizLog]:
    """Store user_answer and assessment_result on a quiz log."""
    quiz_log = db.query(QuizLog).filter(QuizLog.id == quiz_id).first()
    if not quiz_log:
        return None
    quiz_log.user_answer = user_answer
    quiz_log.assessment_result = assessment_result
    db.commit()
    db.refresh(quiz_log)
    return quiz_log


def get_quiz_log_by_id(db: Session, quiz_id: int) -> Optional[QuizLog]:
    """Get a quiz log by ID."""
    return db.query(QuizLog).filter(QuizLog.id == quiz_id).first()


def get_seen_question_ids(
    db: Session, username: str, lesson_id: int, quiz_type: str
) -> List[int]:
    """Get IDs of questions already seen by user for deduplication."""
    rows = (
        db.query(QuizLog.quiz_question_id)
        .filter(
            QuizLog.username == username,
            QuizLog.lesson_id == lesson_id,
            QuizLog.quiz_type == quiz_type,
        )
        .all()
    )
    return [r[0] for r in rows]


def get_quiz_history(
    db: Session, username: str, limit: int = 20, offset: int = 0
) -> List[QuizLog]:
    """Get paginated quiz history for a user."""
    return (
        db.query(QuizLog)
        .filter(QuizLog.username == username)
        .order_by(QuizLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_user_total_quiz_count(db: Session, username: str) -> int:
    """Total number of quizzes for a user (for MEMORIZE formula)."""
    return db.query(QuizLog).filter(QuizLog.username == username).count()


def get_latest_pending_quiz(db: Session, username: str) -> Optional[QuizLog]:
    """Get the most recent unanswered quiz for a user."""
    return (
        db.query(QuizLog)
        .filter(
            QuizLog.username == username,
            QuizLog.assessment_result.is_(None),
        )
        .order_by(QuizLog.created_at.desc())
        .first()
    )


def get_recent_quiz_types(db: Session, username: str, limit: int = 3) -> List[str]:
    """Get the most recently used quiz types for rotation."""
    rows = (
        db.query(QuizLog.quiz_type)
        .filter(QuizLog.username == username)
        .order_by(QuizLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [r[0] for r in rows]


def get_all_quiz_logs(db: Session, username: str) -> List[QuizLog]:
    """All quiz logs ordered by created_at (for topic matrix)."""
    return (
        db.query(QuizLog)
        .filter(QuizLog.username == username)
        .order_by(QuizLog.created_at.asc())
        .all()
    )


def get_quiz_stats(db: Session, username: str) -> dict:
    """Get quiz statistics: total, correct, accuracy."""
    total = db.query(QuizLog).filter(QuizLog.username == username).count()
    correct = (
        db.query(QuizLog)
        .filter(QuizLog.username == username, QuizLog.assessment_result == "correct")
        .count()
    )
    accuracy = correct / total if total > 0 else 0.0
    return {"total": total, "correct": correct, "accuracy": round(accuracy, 4)}
