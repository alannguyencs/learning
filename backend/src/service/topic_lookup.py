"""Topic-lesson resolution utility — syncs from DB on startup."""

import logging
from typing import Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_lesson_to_topic: Dict[int, str] = {}
_topic_to_lessons: Dict[str, List[int]] = {}
_topic_names: Dict[str, str] = {}
_lesson_names: Dict[int, str] = {}
_lesson_filenames: Dict[int, str] = {}


def clear_cache() -> None:
    """Clear all in-memory caches (useful for testing)."""
    _lesson_to_topic.clear()
    _topic_to_lessons.clear()
    _topic_names.clear()
    _lesson_names.clear()
    _lesson_filenames.clear()


def get_topic_for_lesson(lesson_id: int) -> Optional[str]:
    """Resolve a lesson_id to its topic_id."""
    return _lesson_to_topic.get(lesson_id)


def get_lessons_for_topic(topic_id: str) -> List[int]:
    """Get all lesson_ids belonging to a topic."""
    return _topic_to_lessons.get(topic_id, [])


def get_all_topic_ids() -> List[str]:
    """Return all known topic IDs."""
    return list(_topic_to_lessons.keys())


def get_topic_name(topic_id: str) -> str:
    """Return human-readable topic name."""
    return _topic_names.get(topic_id, topic_id)


def get_lesson_name(lesson_id: int) -> str:
    """Return human-readable lesson name."""
    return _lesson_names.get(lesson_id, f"Lesson {lesson_id}")


def get_lesson_filename(lesson_id: int) -> str:
    """Return lesson filename."""
    return _lesson_filenames.get(lesson_id, "")


def get_lesson_count(topic_id: str) -> int:
    """Return number of lessons in a topic."""
    return len(_topic_to_lessons.get(topic_id, []))


def register_topic(
    topic_id: str,
    topic_name: str,
    lesson_id: int,
    lesson_name: str,
    lesson_filename: str,
) -> None:
    """Register a topic/lesson in the in-memory cache if not already present."""
    if topic_id not in _topic_to_lessons:
        _topic_to_lessons[topic_id] = []
        logger.info("Registered new topic: %s (%s)", topic_id, topic_name)
    if topic_id not in _topic_names or _topic_names[topic_id] == topic_id:
        _topic_names[topic_id] = topic_name

    if lesson_id not in _lesson_to_topic:
        _lesson_to_topic[lesson_id] = topic_id
    if lesson_id not in _lesson_names:
        _lesson_names[lesson_id] = lesson_name
    if lesson_id not in _lesson_filenames and lesson_filename:
        _lesson_filenames[lesson_id] = lesson_filename
    if lesson_id not in _topic_to_lessons[topic_id]:
        _topic_to_lessons[topic_id].append(lesson_id)


def sync_from_db(db: Session) -> None:
    """Sync in-memory topic cache from lessons table (primary) and quiz_questions (fallback)."""
    try:
        # Primary: read from lessons table
        lesson_rows = db.execute(
            text("SELECT id, topic, topic_name, title FROM lessons")
        ).fetchall()
        for row in lesson_rows:
            lesson_id, topic_id, topic_name, title = row
            register_topic(
                topic_id=topic_id,
                topic_name=topic_name or topic_id,
                lesson_id=lesson_id,
                lesson_name=title,
                lesson_filename="",
            )
        logger.info("Synced %d lesson rows from lessons table", len(lesson_rows))

        # Fallback: pick up any quiz_questions entries not in lessons table
        qq_rows = db.execute(
            text(
                "SELECT DISTINCT topic_id, topic_name, lesson_id, lesson_name, lesson_filename "
                "FROM quiz_questions"
            )
        ).fetchall()
        for row in qq_rows:
            topic_id, topic_name, lesson_id, lesson_name, lesson_filename = row
            register_topic(
                topic_id=topic_id,
                topic_name=topic_name or topic_id,
                lesson_id=lesson_id,
                lesson_name=lesson_name or f"Lesson {lesson_id}",
                lesson_filename=lesson_filename or "",
            )
        logger.info("Synced %d topic/lesson rows from quiz_questions", len(qq_rows))
    except Exception as e:
        logger.error("Failed to sync topics from DB: %s", e)
