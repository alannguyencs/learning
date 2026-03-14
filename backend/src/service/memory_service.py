"""Memory service — updates topic, lesson, and question MEMORIZE state."""

import logging

from sqlalchemy.orm import Session

from src.crud.crud_topic_memory import update_memory_on_quiz_result as update_topic_memory
from src.crud.crud_lesson_memory import update_memory_on_quiz_result as update_lesson_memory
from src.crud.crud_question_memory import (
    update_memory_on_quiz_result as update_question_memory,
)

logger = logging.getLogger(__name__)


def update_memory(
    db: Session,
    username: str,
    topic_id: str,
    lesson_id: int,
    quiz_question_id: int,
    is_correct: bool,
    current_quiz_count: int,
) -> None:
    """Update UserTopicMemory, UserLessonMemory, and UserQuestionMemory."""
    update_topic_memory(db, username, topic_id, is_correct, current_quiz_count)
    update_lesson_memory(db, username, lesson_id, is_correct, current_quiz_count)
    update_question_memory(db, username, quiz_question_id, is_correct, current_quiz_count)
