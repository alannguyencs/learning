"""Tests for memory service."""

from src.crud.crud_user import create_user
from src.crud.crud_topic_memory import get_or_create_memory as get_or_create_topic
from src.crud.crud_lesson_memory import get_or_create_memory as get_or_create_lesson
from src.crud.crud_question_memory import (
    get_or_create_memory as get_or_create_question,
)
from src.models.quiz_question import QuizQuestion
from src.service.memory_service import update_memory


def _create_question(db, topic_id="t1", lesson_id=1):
    q = QuizQuestion(
        topic_id=topic_id,
        lesson_id=lesson_id,
        lesson_filename="test.md",
        quiz_type="recall",
        question="Q?",
        quiz_learnt="L",
        option_a="A",
        option_b="B",
        option_c="C",
        option_d="D",
        correct_options=["B"],
        response_to_user_option_a="eA",
        response_to_user_option_b="eB",
        response_to_user_option_c="eC",
        response_to_user_option_d="eD",
        quiz_take_away="TK",
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


class TestMemoryUpdate:
    """Tests for three-level memory update."""

    def test_correct_reduces_forgetting_rate(self, db_session):
        """n *= 0.7 at all three levels."""
        create_user(db_session, "testuser", "hash")
        q = _create_question(db_session)
        get_or_create_topic(db_session, "testuser", "t1")
        get_or_create_lesson(db_session, "testuser", "t1", 1)

        update_memory(db_session, "testuser", "t1", 1, q.id, True, 10)

        topic = get_or_create_topic(db_session, "testuser", "t1")
        lesson = get_or_create_lesson(db_session, "testuser", "t1", 1)
        question = get_or_create_question(db_session, "testuser", q.id)
        assert topic.forgetting_rate < 0.3
        assert lesson.forgetting_rate < 0.3
        assert question.forgetting_rate < 0.3

    def test_incorrect_increases_forgetting_rate(self, db_session):
        """n *= 1.2 at all three levels."""
        create_user(db_session, "testuser", "hash")
        q = _create_question(db_session)
        get_or_create_topic(db_session, "testuser", "t1")
        get_or_create_lesson(db_session, "testuser", "t1", 1)

        update_memory(db_session, "testuser", "t1", 1, q.id, False, 10)

        topic = get_or_create_topic(db_session, "testuser", "t1")
        lesson = get_or_create_lesson(db_session, "testuser", "t1", 1)
        question = get_or_create_question(db_session, "testuser", q.id)
        assert topic.forgetting_rate > 0.3
        assert lesson.forgetting_rate > 0.3
        assert question.forgetting_rate > 0.3

    def test_forgetting_rate_capped(self, db_session):
        """n never exceeds 1.5."""
        create_user(db_session, "testuser", "hash")
        q = _create_question(db_session)
        topic = get_or_create_topic(db_session, "testuser", "t1")
        topic.forgetting_rate = 1.4
        db_session.commit()
        lesson = get_or_create_lesson(db_session, "testuser", "t1", 1)
        lesson.forgetting_rate = 1.4
        db_session.commit()

        update_memory(db_session, "testuser", "t1", 1, q.id, False, 10)

        topic = get_or_create_topic(db_session, "testuser", "t1")
        lesson = get_or_create_lesson(db_session, "testuser", "t1", 1)
        question = get_or_create_question(db_session, "testuser", q.id)
        assert topic.forgetting_rate <= 1.5
        assert lesson.forgetting_rate <= 1.5
        assert question.forgetting_rate <= 1.5

    def test_all_three_levels_updated(self, db_session):
        """Topic, lesson, AND question memory updated in same call."""
        create_user(db_session, "testuser", "hash")
        q = _create_question(db_session)
        get_or_create_topic(db_session, "testuser", "t1")
        get_or_create_lesson(db_session, "testuser", "t1", 1)

        update_memory(db_session, "testuser", "t1", 1, q.id, True, 10)

        topic = get_or_create_topic(db_session, "testuser", "t1")
        lesson = get_or_create_lesson(db_session, "testuser", "t1", 1)
        question = get_or_create_question(db_session, "testuser", q.id)
        assert topic.review_count == 1
        assert lesson.review_count == 1
        assert question.review_count == 1

    def test_counters_incremented(self, db_session):
        """review_count and correct_count updated at all levels."""
        create_user(db_session, "testuser", "hash")
        q = _create_question(db_session)
        get_or_create_topic(db_session, "testuser", "t1")
        get_or_create_lesson(db_session, "testuser", "t1", 1)

        update_memory(db_session, "testuser", "t1", 1, q.id, True, 10)

        topic = get_or_create_topic(db_session, "testuser", "t1")
        question = get_or_create_question(db_session, "testuser", q.id)
        assert topic.review_count == 1
        assert topic.correct_count == 1
        assert question.review_count == 1
        assert question.correct_count == 1
