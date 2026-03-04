"""Quiz Selector — MEMORIZE-based two-level scheduling.

Step 1: select_topic_for_quiz()  — topic with lowest m(t)
Step 2: select_lesson_for_quiz() — lesson with lowest m(t) within topic
Step 3: select_quiz_type()       — rotate through 4 types
Step 4: select question from bank (dedup)
"""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from src.crud.crud_quiz_log import (
    get_seen_question_ids,
    get_recent_quiz_types,
    get_user_total_quiz_count,
)
from src.crud.crud_quiz_question import get_question, get_question_count
from src.crud.crud_topic_memory import get_all_memory_states
from src.crud.crud_lesson_memory import (
    get_or_create_memory as get_or_create_lesson_memory,
    get_lesson_memories_for_topic,
)
from src.models.quiz_question import QuizQuestion
from src.service.topic_lookup import (
    get_all_topic_ids,
    get_lessons_for_topic,
    get_topic_for_lesson,
)

logger = logging.getLogger(__name__)

RECALL_NEVER_REVIEWED = 0.0
QUIZ_TYPES_ROTATION = ["recall", "understanding", "application", "analysis"]


def select_topic_for_quiz(db: Session, username: str) -> Optional[str]:
    """MEMORIZE: return the topic with the lowest recall m(t).

    Never-reviewed topics get m(t) = 0.0 to prioritize first review.
    """
    current_quiz_count = get_user_total_quiz_count(db, username)
    existing = {r.topic_id: r for r in get_all_memory_states(db, username)}

    best_topic = None
    lowest_recall = float("inf")

    for topic_id in get_all_topic_ids():
        if topic_id in existing:
            recall = existing[topic_id].recall_probability(current_quiz_count)
        else:
            recall = RECALL_NEVER_REVIEWED

        if recall < lowest_recall:
            lowest_recall = recall
            best_topic = topic_id

    return best_topic


def select_lesson_for_quiz(db: Session, username: str, topic_id: str) -> Optional[int]:
    """MEMORIZE: return the lesson with the lowest recall m(t) within a topic.

    Never-reviewed lessons get m(t) = 0.0 to prioritize first review.
    Only considers lessons that have questions in the bank.
    """
    current_quiz_count = get_user_total_quiz_count(db, username)
    lesson_ids = get_lessons_for_topic(topic_id)

    if not lesson_ids:
        return None

    existing = {r.lesson_id: r for r in get_lesson_memories_for_topic(db, username, topic_id)}

    best_lesson = None
    lowest_recall = float("inf")

    for lid in lesson_ids:
        if get_question_count(db, lid) == 0:
            continue

        if lid in existing:
            recall = existing[lid].recall_probability(current_quiz_count)
        else:
            recall = RECALL_NEVER_REVIEWED

        if recall < lowest_recall:
            lowest_recall = recall
            best_lesson = lid

    return best_lesson


def select_quiz_type(db: Session, username: str, exclude_recent: int = 3) -> str:
    """Rotate through quiz types, skipping recently used ones."""
    recent_types = get_recent_quiz_types(db, username, limit=exclude_recent)

    for quiz_type in QUIZ_TYPES_ROTATION:
        if quiz_type not in recent_types:
            return quiz_type

    return QUIZ_TYPES_ROTATION[0]


def select_quiz(
    db: Session,
    username: str,
    topic_id: Optional[str] = None,
    lesson_id: Optional[int] = None,
) -> Optional[QuizQuestion]:
    """Main entry point — resolves scope, selects topic/lesson/type/question.

    Scope resolution:
    - lesson_id provided → skip both selectors
    - topic_id provided → skip topic selector
    - neither → use both selectors
    """
    # Resolve scope
    if lesson_id is not None:
        resolved_topic = get_topic_for_lesson(lesson_id)
        resolved_lesson = lesson_id
    elif topic_id is not None:
        resolved_topic = topic_id
        resolved_lesson = select_lesson_for_quiz(db, username, topic_id)
    else:
        resolved_topic = select_topic_for_quiz(db, username)
        if resolved_topic is None:
            return None
        resolved_lesson = select_lesson_for_quiz(db, username, resolved_topic)

    if resolved_lesson is None:
        return None

    # Ensure lesson memory exists
    if resolved_topic:
        get_or_create_lesson_memory(db, username, resolved_topic, resolved_lesson)

    # Select quiz type
    quiz_type = select_quiz_type(db, username)

    # Get question with dedup
    seen_ids = get_seen_question_ids(db, username, resolved_lesson, quiz_type)
    question = get_question(db, resolved_lesson, quiz_type, exclude_ids=seen_ids)

    # If no unseen questions for this type, try without dedup
    if question is None:
        question = get_question(db, resolved_lesson, quiz_type, exclude_ids=None)

    # If still none, try other quiz types
    if question is None:
        for alt_type in QUIZ_TYPES_ROTATION:
            if alt_type == quiz_type:
                continue
            question = get_question(db, resolved_lesson, alt_type, exclude_ids=None)
            if question is not None:
                break

    return question
