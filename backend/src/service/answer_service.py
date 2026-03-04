"""Answer service — grade quiz answer, store result, update memory."""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from src.crud.crud_quiz_log import (
    get_quiz_log_by_id,
    record_quiz_answer,
    get_user_total_quiz_count,
)
from src.crud.crud_quiz_question import get_question_by_id
from src.service.memory_service import update_memory

logger = logging.getLogger(__name__)


def grade_and_update(db: Session, quiz_id: int, user_answer: List[str]) -> Optional[dict]:
    """Grade answer, store user_answer, update both memory levels.

    Returns dict with: is_correct, correct_options, quiz_learnt,
    explanations {A, B, C, D}, quiz_take_away
    """
    quiz_log = get_quiz_log_by_id(db, quiz_id)
    if not quiz_log:
        return None

    if quiz_log.assessment_result is not None:
        return None

    question = get_question_by_id(db, quiz_log.quiz_question_id)
    if not question:
        return None

    # Grade: compare sorted lists (order-independent)
    correct_options = question.correct_options
    is_correct = sorted([a.upper() for a in user_answer]) == sorted(
        [c.upper() for c in correct_options]
    )

    assessment_result = "correct" if is_correct else "incorrect"

    # Store answer on QuizLog
    record_quiz_answer(db, quiz_id, user_answer, assessment_result)

    # Update MEMORIZE memory at both levels
    current_quiz_count = get_user_total_quiz_count(db, quiz_log.username)
    update_memory(
        db,
        quiz_log.username,
        quiz_log.topic_id,
        quiz_log.lesson_id,
        is_correct,
        current_quiz_count,
    )

    return {
        "is_correct": is_correct,
        "correct_options": correct_options,
        "quiz_learnt": question.quiz_learnt,
        "explanations": question.get_explanations(),
        "quiz_take_away": question.quiz_take_away,
    }
