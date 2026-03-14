"""Quiz Selector — MEMORIZE-based scheduling.

Case 1 (lesson_id):  sliding window dedup, random order
Case 2 (topic_id):   question-level recall, lowest m(t) first
Case 3 (neither):    question-level recall across all topics
"""

import logging
import random
from typing import List, Optional

from sqlalchemy.orm import Session

from src.crud.crud_quiz_log import (
    get_recent_question_ids_for_lesson,
    get_recent_question_ids_for_topic,
    get_recent_question_ids_global,
    get_user_total_quiz_count,
)
from src.crud.crud_quiz_question import (
    get_question_count,
    get_question_count_for_topic,
    get_question_for_lesson,
    get_total_question_count,
)
from src.crud.crud_question_memory import get_question_memories_for_ids
from src.crud.crud_lesson_memory import (
    get_or_create_memory as get_or_create_lesson_memory,
)
from src.models.quiz_question import QuizQuestion
from src.service.topic_lookup import get_topic_for_lesson

logger = logging.getLogger(__name__)

RECALL_NEVER_REVIEWED = 0.0
LOOP_SIZE_CAP = 10


def select_question_by_recall(
    db: Session,
    username: str,
    topic_id: Optional[str] = None,
    exclude_ids: Optional[List[int]] = None,
) -> Optional[QuizQuestion]:
    """Select the question with the lowest recall m(t) within scope.

    Never-answered questions get m(t) = 0.0 (highest priority).
    All quiz types are eligible — no type rotation.
    """
    query = db.query(QuizQuestion)
    if topic_id:
        query = query.filter(QuizQuestion.topic_id == topic_id)
    questions = query.all()

    if not questions:
        return None

    exclude_set = set(exclude_ids) if exclude_ids else set()

    qids = [q.id for q in questions]
    existing = {r.quiz_question_id: r for r in get_question_memories_for_ids(db, username, qids)}
    current_quiz_count = get_user_total_quiz_count(db, username)

    # Collect all candidates with their recall scores
    candidates = []
    for q in questions:
        if q.id in exclude_set:
            continue
        mem = existing.get(q.id)
        if mem and mem.review_count > 0:
            recall = mem.recall_probability(current_quiz_count)
        else:
            recall = RECALL_NEVER_REVIEWED
        candidates.append((recall, q))

    if not candidates:
        return None

    # Find lowest recall, then pick randomly among tied candidates
    lowest = min(r for r, _ in candidates)
    tied = [q for r, q in candidates if r == lowest]
    return random.choice(tied)


def select_quiz(
    db: Session,
    username: str,
    topic_id: Optional[str] = None,
    lesson_id: Optional[int] = None,
) -> Optional[QuizQuestion]:
    """Main entry point — resolves scope, selects question.

    Scope resolution:
    - lesson_id provided → sliding window dedup, random order (Case 1)
    - topic_id provided → question-level recall within topic (Case 2)
    - neither → question-level recall across all topics (Case 3)
    """
    # Case 1: lesson-scoped — sliding window dedup, random order
    if lesson_id is not None:
        resolved_topic = get_topic_for_lesson(lesson_id)
        if resolved_topic:
            get_or_create_lesson_memory(db, username, resolved_topic, lesson_id)

        total = get_question_count(db, lesson_id)
        window = max(total - 1, 0)
        exclude_ids = get_recent_question_ids_for_lesson(db, username, lesson_id, window)
        return get_question_for_lesson(db, lesson_id, exclude_ids=exclude_ids or None)

    # Cases 2 & 3: question-level recall selection
    if topic_id is not None:
        total = get_question_count_for_topic(db, topic_id)
    else:
        total = get_total_question_count(db)

    loop_size = min(LOOP_SIZE_CAP, total)
    window = max(loop_size - 1, 0)

    if topic_id is not None:
        exclude_ids = get_recent_question_ids_for_topic(db, username, topic_id, window)
    else:
        exclude_ids = get_recent_question_ids_global(db, username, window)

    return select_question_by_recall(db, username, topic_id=topic_id, exclude_ids=exclude_ids)
