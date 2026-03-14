"""Tests for UserQuestionMemory model and CRUD."""

from src.crud.crud_user import create_user
from src.crud.crud_question_memory import (
    get_or_create_memory,
    get_question_memories_for_ids,
    update_memory_on_quiz_result,
)
from src.models.quiz_question import QuizQuestion


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


class TestQuestionMemoryModel:
    """Tests for UserQuestionMemory recall computation."""

    def test_recall_probability_never_reviewed(self, db_session):
        """Model returns 1.0 when review_count == 0."""
        create_user(db_session, "testuser", "hash")
        q = _create_question(db_session)
        mem = get_or_create_memory(db_session, "testuser", q.id)
        assert mem.recall_probability(100) == 1.0

    def test_recall_probability_decays(self, db_session):
        """m(t) decreases as quizzes_elapsed increases."""
        create_user(db_session, "testuser", "hash")
        q = _create_question(db_session)
        mem = get_or_create_memory(db_session, "testuser", q.id)
        mem.review_count = 1
        mem.last_review_quiz_count = 0
        db_session.commit()

        recall_at_5 = mem.recall_probability(5)
        recall_at_20 = mem.recall_probability(20)
        assert recall_at_5 > recall_at_20

    def test_update_on_correct(self, db_session):
        """Forgetting rate decreases by 30%."""
        create_user(db_session, "testuser", "hash")
        q = _create_question(db_session)
        mem = get_or_create_memory(db_session, "testuser", q.id)
        initial = mem.forgetting_rate
        mem.update_on_correct()
        assert mem.forgetting_rate < initial
        assert abs(mem.forgetting_rate - initial * 0.7) < 1e-6

    def test_update_on_incorrect(self, db_session):
        """Forgetting rate increases by 20%, capped at 1.5."""
        create_user(db_session, "testuser", "hash")
        q = _create_question(db_session)
        mem = get_or_create_memory(db_session, "testuser", q.id)
        initial = mem.forgetting_rate
        mem.update_on_incorrect()
        assert mem.forgetting_rate > initial
        assert abs(mem.forgetting_rate - initial * 1.2) < 1e-6

    def test_forgetting_rate_capped(self, db_session):
        """Forgetting rate never exceeds 1.5."""
        create_user(db_session, "testuser", "hash")
        q = _create_question(db_session)
        mem = get_or_create_memory(db_session, "testuser", q.id)
        mem.forgetting_rate = 1.4
        mem.update_on_incorrect()
        assert mem.forgetting_rate <= 1.5


class TestQuestionMemoryCRUD:
    """Tests for CRUD operations on UserQuestionMemory."""

    def test_get_or_create_memory_creates(self, db_session):
        """Creates record if not exists."""
        create_user(db_session, "testuser", "hash")
        q = _create_question(db_session)
        mem = get_or_create_memory(db_session, "testuser", q.id)
        assert mem.username == "testuser"
        assert mem.quiz_question_id == q.id
        assert mem.review_count == 0

    def test_get_or_create_memory_returns_existing(self, db_session):
        """Returns existing record on second call."""
        create_user(db_session, "testuser", "hash")
        q = _create_question(db_session)
        mem1 = get_or_create_memory(db_session, "testuser", q.id)
        mem2 = get_or_create_memory(db_session, "testuser", q.id)
        assert mem1.id == mem2.id

    def test_get_question_memories_for_ids(self, db_session):
        """Batch load returns memories for given IDs."""
        create_user(db_session, "testuser", "hash")
        q1 = _create_question(db_session)
        q2 = _create_question(db_session)
        get_or_create_memory(db_session, "testuser", q1.id)
        get_or_create_memory(db_session, "testuser", q2.id)

        results = get_question_memories_for_ids(db_session, "testuser", [q1.id, q2.id])
        assert len(results) == 2

    def test_update_memory_on_correct(self, db_session):
        """Updates counters and forgetting rate on correct answer."""
        create_user(db_session, "testuser", "hash")
        q = _create_question(db_session)
        mem = update_memory_on_quiz_result(db_session, "testuser", q.id, True, 10)
        assert mem.review_count == 1
        assert mem.correct_count == 1
        assert mem.forgetting_rate < 0.3
        assert mem.last_review_quiz_count == 10

    def test_update_memory_on_incorrect(self, db_session):
        """Updates counters and forgetting rate on incorrect answer."""
        create_user(db_session, "testuser", "hash")
        q = _create_question(db_session)
        mem = update_memory_on_quiz_result(db_session, "testuser", q.id, False, 10)
        assert mem.review_count == 1
        assert mem.correct_count == 0
        assert mem.forgetting_rate > 0.3
