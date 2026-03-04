"""Tests for memory CRUD operations."""

from src.crud.crud_user import create_user
from src.crud.crud_topic_memory import (
    get_or_create_memory as get_or_create_topic,
    update_memory_on_quiz_result as update_topic,
    get_all_memory_states,
)
from src.crud.crud_lesson_memory import (
    get_or_create_memory as get_or_create_lesson,
    update_memory_on_quiz_result as update_lesson,
    get_lesson_memories_for_topic,
)


class TestTopicMemoryCRUD:
    """Tests for topic memory CRUD."""

    def test_get_or_create_new(self, db_session):
        """Creates with default n=0.3."""
        create_user(db_session, "testuser", "hash")
        mem = get_or_create_topic(db_session, "testuser", "t1")
        assert mem.forgetting_rate == 0.3
        assert mem.review_count == 0

    def test_get_or_create_existing(self, db_session):
        """Returns existing record."""
        create_user(db_session, "testuser", "hash")
        mem1 = get_or_create_topic(db_session, "testuser", "t1")
        mem2 = get_or_create_topic(db_session, "testuser", "t1")
        assert mem1.id == mem2.id

    def test_update_on_correct(self, db_session):
        """n decreases, correct_count increments."""
        create_user(db_session, "testuser", "hash")
        mem = update_topic(db_session, "testuser", "t1", True, 10)
        assert mem.forgetting_rate < 0.3
        assert mem.correct_count == 1
        assert mem.review_count == 1

    def test_update_on_incorrect(self, db_session):
        """n increases on incorrect."""
        create_user(db_session, "testuser", "hash")
        mem = update_topic(db_session, "testuser", "t1", False, 10)
        assert mem.forgetting_rate > 0.3
        assert mem.correct_count == 0
        assert mem.review_count == 1

    def test_get_all_memory_states(self, db_session):
        """Returns all topic memories for user."""
        create_user(db_session, "testuser", "hash")
        get_or_create_topic(db_session, "testuser", "t1")
        get_or_create_topic(db_session, "testuser", "t2")
        states = get_all_memory_states(db_session, "testuser")
        assert len(states) == 2


class TestLessonMemoryCRUD:
    """Tests for lesson memory CRUD."""

    def test_get_or_create_new(self, db_session):
        """Creates with default n=0.3."""
        create_user(db_session, "testuser", "hash")
        mem = get_or_create_lesson(db_session, "testuser", "t1", 1)
        assert mem.forgetting_rate == 0.3
        assert mem.topic_id == "t1"

    def test_get_lesson_memories_for_topic(self, db_session):
        """Returns only lessons in topic."""
        create_user(db_session, "testuser", "hash")
        get_or_create_lesson(db_session, "testuser", "t1", 1)
        get_or_create_lesson(db_session, "testuser", "t1", 2)
        get_or_create_lesson(db_session, "testuser", "t2", 3)
        lessons = get_lesson_memories_for_topic(db_session, "testuser", "t1")
        assert len(lessons) == 2

    def test_update_on_correct(self, db_session):
        """Lesson memory updates correctly."""
        create_user(db_session, "testuser", "hash")
        get_or_create_lesson(db_session, "testuser", "t1", 1)
        mem = update_lesson(db_session, "testuser", 1, True, 10)
        assert mem is not None
        assert mem.forgetting_rate < 0.3

    def test_update_nonexistent_returns_none(self, db_session):
        """Returns None if lesson memory doesn't exist."""
        create_user(db_session, "testuser", "hash")
        result = update_lesson(db_session, "testuser", 999, True, 10)
        assert result is None
