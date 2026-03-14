"""CRUD operations for UserTopicMemory — MEMORIZE algorithm state."""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from src.models.user_topic_memory import UserTopicMemory

logger = logging.getLogger(__name__)

DEFAULT_N_INITIAL = 0.3
ALPHA = 0.3
BETA = 0.2


def get_or_create_memory(db: Session, username: str, topic_id: str) -> UserTopicMemory:
    """Get or lazily create a topic memory record with default n=0.3."""
    record = (
        db.query(UserTopicMemory)
        .filter(
            UserTopicMemory.username == username,
            UserTopicMemory.topic_id == topic_id,
        )
        .first()
    )
    if record:
        return record

    record = UserTopicMemory(
        username=username,
        topic_id=topic_id,
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
    topic_id: str,
    is_correct: bool,
    current_quiz_count: int,
) -> Optional[UserTopicMemory]:
    """Update topic memory after a quiz result."""
    record = get_or_create_memory(db, username, topic_id)

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


def get_all_memory_states(db: Session, username: str) -> List[UserTopicMemory]:
    """Fetch all topic memory records for a user."""
    return db.query(UserTopicMemory).filter(UserTopicMemory.username == username).all()


def get_recall_probabilities(
    db: Session, username: str, current_quiz_count: int
) -> Dict[str, float]:
    """Return {topic_id: recall_probability} for all topics with records."""
    records = get_all_memory_states(db, username)
    return {r.topic_id: r.recall_probability(current_quiz_count) for r in records}
