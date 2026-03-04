"""Topic-lesson resolution utility — seeds from topics.json, syncs from DB."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_TOPICS_PATH = Path(__file__).parent.parent.parent / "resources" / "topics.json"

_lesson_to_topic: Dict[int, str] = {}
_topic_to_lessons: Dict[str, List[int]] = {}
_topic_names: Dict[str, str] = {}
_lesson_names: Dict[int, str] = {}
_lesson_filenames: Dict[int, str] = {}


def _load_topics() -> None:
    """Load and cache the topic-lesson mapping."""
    global _lesson_to_topic, _topic_to_lessons, _topic_names, _lesson_names, _lesson_filenames
    try:
        with open(_TOPICS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        for topic in data.get("topics", []):
            tid = topic["id"]
            lids = topic.get("lesson_ids", [])
            _topic_to_lessons[tid] = lids
            _topic_names[tid] = topic.get("name", tid)
            for lid in lids:
                _lesson_to_topic[lid] = tid

        for lid_str, info in data.get("lessons", {}).items():
            lid = int(lid_str)
            _lesson_names[lid] = info.get("name", f"Lesson {lid}")
            _lesson_filenames[lid] = info.get("filename", "")

        logger.info(
            f"Loaded topic mapping: {len(_topic_to_lessons)} topics, "
            f"{len(_lesson_to_topic)} lessons"
        )
    except Exception as e:
        logger.error(f"Failed to load topics.json: {e}")


_load_topics()


def reload_topics() -> None:
    """Reload topics from disk (useful for testing)."""
    global _lesson_to_topic, _topic_to_lessons, _topic_names, _lesson_names, _lesson_filenames
    _lesson_to_topic.clear()
    _topic_to_lessons.clear()
    _topic_names.clear()
    _lesson_names.clear()
    _lesson_filenames.clear()
    _load_topics()


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
        logger.info(f"Registered new topic: {topic_id} ({topic_name})")
    if topic_id not in _topic_names:
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
    """Sync in-memory topic cache from quiz_questions table."""
    try:
        rows = db.execute(
            text(
                "SELECT DISTINCT topic_id, topic_name, lesson_id, lesson_name, lesson_filename "
                "FROM quiz_questions"
            )
        ).fetchall()
        for row in rows:
            topic_id, topic_name, lesson_id, lesson_name, lesson_filename = row
            register_topic(
                topic_id=topic_id,
                topic_name=topic_name or topic_id,
                lesson_id=lesson_id,
                lesson_name=lesson_name or f"Lesson {lesson_id}",
                lesson_filename=lesson_filename or "",
            )
        logger.info(f"Synced {len(rows)} topic/lesson rows from DB")
    except Exception as e:
        logger.error(f"Failed to sync topics from DB: {e}")
