"""Tests for memory service."""

from src.crud.crud_user import create_user
from src.crud.crud_topic_memory import get_or_create_memory as get_or_create_topic
from src.crud.crud_lesson_memory import get_or_create_memory as get_or_create_lesson
from src.service.memory_service import update_memory


class TestMemoryUpdate:
    """Tests for dual-level memory update."""

    def test_correct_reduces_forgetting_rate(self, db_session):
        """n *= 0.7 at both levels."""
        create_user(db_session, "testuser", "hash")
        get_or_create_topic(db_session, "testuser", "t1")
        get_or_create_lesson(db_session, "testuser", "t1", 1)

        update_memory(db_session, "testuser", "t1", 1, True, 10)

        topic = get_or_create_topic(db_session, "testuser", "t1")
        lesson = get_or_create_lesson(db_session, "testuser", "t1", 1)
        assert topic.forgetting_rate < 0.3
        assert lesson.forgetting_rate < 0.3

    def test_incorrect_increases_forgetting_rate(self, db_session):
        """n *= 1.2 at both levels."""
        create_user(db_session, "testuser", "hash")
        get_or_create_topic(db_session, "testuser", "t1")
        get_or_create_lesson(db_session, "testuser", "t1", 1)

        update_memory(db_session, "testuser", "t1", 1, False, 10)

        topic = get_or_create_topic(db_session, "testuser", "t1")
        lesson = get_or_create_lesson(db_session, "testuser", "t1", 1)
        assert topic.forgetting_rate > 0.3
        assert lesson.forgetting_rate > 0.3

    def test_forgetting_rate_capped(self, db_session):
        """n never exceeds 1.5."""
        create_user(db_session, "testuser", "hash")
        topic = get_or_create_topic(db_session, "testuser", "t1")
        topic.forgetting_rate = 1.4
        db_session.commit()
        lesson = get_or_create_lesson(db_session, "testuser", "t1", 1)
        lesson.forgetting_rate = 1.4
        db_session.commit()

        update_memory(db_session, "testuser", "t1", 1, False, 10)

        topic = get_or_create_topic(db_session, "testuser", "t1")
        lesson = get_or_create_lesson(db_session, "testuser", "t1", 1)
        assert topic.forgetting_rate <= 1.5
        assert lesson.forgetting_rate <= 1.5

    def test_both_levels_updated(self, db_session):
        """Topic AND lesson memory updated in same call."""
        create_user(db_session, "testuser", "hash")
        get_or_create_topic(db_session, "testuser", "t1")
        get_or_create_lesson(db_session, "testuser", "t1", 1)

        update_memory(db_session, "testuser", "t1", 1, True, 10)

        topic = get_or_create_topic(db_session, "testuser", "t1")
        lesson = get_or_create_lesson(db_session, "testuser", "t1", 1)
        assert topic.review_count == 1
        assert lesson.review_count == 1

    def test_counters_incremented(self, db_session):
        """review_count and correct_count updated."""
        create_user(db_session, "testuser", "hash")
        get_or_create_topic(db_session, "testuser", "t1")
        get_or_create_lesson(db_session, "testuser", "t1", 1)

        update_memory(db_session, "testuser", "t1", 1, True, 10)

        topic = get_or_create_topic(db_session, "testuser", "t1")
        assert topic.review_count == 1
        assert topic.correct_count == 1
