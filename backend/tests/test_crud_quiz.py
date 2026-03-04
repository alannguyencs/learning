"""Tests for quiz CRUD operations."""

from src.crud.crud_user import create_user
from src.crud.crud_quiz_log import (
    create_quiz_log,
    record_quiz_answer,
    get_seen_question_ids,
    get_user_total_quiz_count,
    get_quiz_log_by_id,
    get_quiz_stats,
)
from src.crud.crud_quiz_question import (
    get_question,
    get_question_count,
)
from src.models.quiz_question import QuizQuestion


def _create_test_question(db, topic_id="t1", lesson_id=1, quiz_type="recall"):
    """Helper to create a test quiz question."""
    q = QuizQuestion(
        topic_id=topic_id,
        lesson_id=lesson_id,
        lesson_filename="test.md",
        quiz_type=quiz_type,
        question="What is X?",
        quiz_learnt="Learning about X",
        option_a="A answer",
        option_b="B answer",
        option_c="C answer",
        option_d="D answer",
        correct_options=["B"],
        response_to_user_option_a="A is wrong because...",
        response_to_user_option_b="B is correct because...",
        response_to_user_option_c="C is wrong because...",
        response_to_user_option_d="D is wrong because...",
        quiz_take_away="Key takeaway",
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


class TestQuizQuestionCRUD:
    """Tests for quiz question CRUD."""

    def test_get_question_matching(self, db_session):
        """Returns matching question."""
        q = _create_test_question(db_session)
        result = get_question(db_session, lesson_id=1, quiz_type="recall")
        assert result is not None
        assert result.id == q.id

    def test_get_question_excludes_ids(self, db_session):
        """Respects exclude list."""
        q1 = _create_test_question(db_session)
        q2 = _create_test_question(db_session)
        result = get_question(db_session, lesson_id=1, quiz_type="recall", exclude_ids=[q1.id])
        assert result.id == q2.id

    def test_get_question_no_match(self, db_session):
        """Returns None when no match."""
        result = get_question(db_session, lesson_id=999, quiz_type="recall")
        assert result is None

    def test_get_question_count(self, db_session):
        """Correct count."""
        _create_test_question(db_session)
        _create_test_question(db_session)
        assert get_question_count(db_session, lesson_id=1) == 2


class TestQuizLogCRUD:
    """Tests for quiz log CRUD."""

    def test_create_quiz_log(self, db_session):
        """Inserts pending log."""
        create_user(db_session, "testuser", "hash")
        q = _create_test_question(db_session)
        log = create_quiz_log(db_session, "testuser", q.id, "t1", 1, "recall")
        assert log.id is not None
        assert log.assessment_result is None

    def test_record_answer(self, db_session):
        """Updates user_answer and assessment_result."""
        create_user(db_session, "testuser", "hash")
        q = _create_test_question(db_session)
        log = create_quiz_log(db_session, "testuser", q.id, "t1", 1, "recall")
        updated = record_quiz_answer(db_session, log.id, ["B"], "correct")
        assert updated.user_answer == ["B"]
        assert updated.assessment_result == "correct"

    def test_get_seen_question_ids(self, db_session):
        """Returns correct dedup list."""
        create_user(db_session, "testuser", "hash")
        q = _create_test_question(db_session)
        create_quiz_log(db_session, "testuser", q.id, "t1", 1, "recall")
        seen = get_seen_question_ids(db_session, "testuser", 1, "recall")
        assert q.id in seen

    def test_get_total_quiz_count(self, db_session):
        """Correct total."""
        create_user(db_session, "testuser", "hash")
        q = _create_test_question(db_session)
        create_quiz_log(db_session, "testuser", q.id, "t1", 1, "recall")
        create_quiz_log(db_session, "testuser", q.id, "t1", 1, "recall")
        assert get_user_total_quiz_count(db_session, "testuser") == 2

    def test_get_quiz_stats(self, db_session):
        """Correct stats computation."""
        create_user(db_session, "testuser", "hash")
        q = _create_test_question(db_session)
        log1 = create_quiz_log(db_session, "testuser", q.id, "t1", 1, "recall")
        log2 = create_quiz_log(db_session, "testuser", q.id, "t1", 1, "recall")
        record_quiz_answer(db_session, log1.id, ["B"], "correct")
        record_quiz_answer(db_session, log2.id, ["A"], "incorrect")
        stats = get_quiz_stats(db_session, "testuser")
        assert stats["total"] == 2
        assert stats["correct"] == 1
        assert stats["accuracy"] == 0.5
