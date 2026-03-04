"""Tests for answer service."""

from src.crud.crud_user import create_user
from src.crud.crud_quiz_log import create_quiz_log, get_quiz_log_by_id
from src.crud.crud_topic_memory import get_or_create_memory as get_or_create_topic
from src.crud.crud_lesson_memory import get_or_create_memory as get_or_create_lesson
from src.models.quiz_question import QuizQuestion
from src.service.answer_service import grade_and_update


def _create_question(db, correct_options=None):
    """Helper to create test quiz question."""
    if correct_options is None:
        correct_options = ["B"]
    q = QuizQuestion(
        topic_id="t1", lesson_id=1, lesson_filename="test.md",
        quiz_type="recall", question="What is X?",
        quiz_learnt="Learning about X",
        option_a="A answer", option_b="B answer",
        option_c="C answer", option_d="D answer",
        correct_options=correct_options,
        response_to_user_option_a="Explanation A",
        response_to_user_option_b="Explanation B",
        response_to_user_option_c="Explanation C",
        response_to_user_option_d="Explanation D",
        quiz_take_away="Key takeaway",
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


class TestAnswerGrading:
    """Tests for answer grading."""

    def test_grade_single_correct(self, db_session):
        """["B"] matches ["B"]."""
        create_user(db_session, "testuser", "hash")
        get_or_create_topic(db_session, "testuser", "t1")
        get_or_create_lesson(db_session, "testuser", "t1", 1)
        q = _create_question(db_session, correct_options=["B"])
        log = create_quiz_log(db_session, "testuser", q.id, "t1", 1, "recall")

        result = grade_and_update(db_session, log.id, ["B"])
        assert result["is_correct"] is True

    def test_grade_single_incorrect(self, db_session):
        """["A"] doesn't match ["B"]."""
        create_user(db_session, "testuser", "hash")
        get_or_create_topic(db_session, "testuser", "t1")
        get_or_create_lesson(db_session, "testuser", "t1", 1)
        q = _create_question(db_session, correct_options=["B"])
        log = create_quiz_log(db_session, "testuser", q.id, "t1", 1, "recall")

        result = grade_and_update(db_session, log.id, ["A"])
        assert result["is_correct"] is False

    def test_grade_multi_correct(self, db_session):
        """["A", "C"] matches ["C", "A"] (order-independent)."""
        create_user(db_session, "testuser", "hash")
        get_or_create_topic(db_session, "testuser", "t1")
        get_or_create_lesson(db_session, "testuser", "t1", 1)
        q = _create_question(db_session, correct_options=["A", "C"])
        log = create_quiz_log(db_session, "testuser", q.id, "t1", 1, "recall")

        result = grade_and_update(db_session, log.id, ["C", "A"])
        assert result["is_correct"] is True

    def test_grade_multi_partial(self, db_session):
        """["A"] doesn't match ["A", "C"] (partial = incorrect)."""
        create_user(db_session, "testuser", "hash")
        get_or_create_topic(db_session, "testuser", "t1")
        get_or_create_lesson(db_session, "testuser", "t1", 1)
        q = _create_question(db_session, correct_options=["A", "C"])
        log = create_quiz_log(db_session, "testuser", q.id, "t1", 1, "recall")

        result = grade_and_update(db_session, log.id, ["A"])
        assert result["is_correct"] is False

    def test_user_answer_stored(self, db_session):
        """user_answer saved on QuizLog."""
        create_user(db_session, "testuser", "hash")
        get_or_create_topic(db_session, "testuser", "t1")
        get_or_create_lesson(db_session, "testuser", "t1", 1)
        q = _create_question(db_session)
        log = create_quiz_log(db_session, "testuser", q.id, "t1", 1, "recall")

        grade_and_update(db_session, log.id, ["B"])
        updated = get_quiz_log_by_id(db_session, log.id)
        assert updated.user_answer == ["B"]

    def test_returns_all_explanations(self, db_session):
        """Response includes all 4 explanations."""
        create_user(db_session, "testuser", "hash")
        get_or_create_topic(db_session, "testuser", "t1")
        get_or_create_lesson(db_session, "testuser", "t1", 1)
        q = _create_question(db_session)
        log = create_quiz_log(db_session, "testuser", q.id, "t1", 1, "recall")

        result = grade_and_update(db_session, log.id, ["B"])
        assert "A" in result["explanations"]
        assert "B" in result["explanations"]
        assert "C" in result["explanations"]
        assert "D" in result["explanations"]
        assert result["quiz_learnt"] == "Learning about X"
        assert result["quiz_take_away"] == "Key takeaway"

    def test_already_answered_returns_none(self, db_session):
        """Returns None for already-answered quiz."""
        create_user(db_session, "testuser", "hash")
        get_or_create_topic(db_session, "testuser", "t1")
        get_or_create_lesson(db_session, "testuser", "t1", 1)
        q = _create_question(db_session)
        log = create_quiz_log(db_session, "testuser", q.id, "t1", 1, "recall")

        grade_and_update(db_session, log.id, ["B"])
        result = grade_and_update(db_session, log.id, ["A"])
        assert result is None
