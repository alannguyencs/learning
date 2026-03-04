"""Tests for quiz ORM models."""

from src.models import QuizQuestion, QuizLog, UserTopicMemory, UserLessonMemory


def test_quiz_question_columns():
    """All flat columns present on QuizQuestion."""
    columns = {c.name for c in QuizQuestion.__table__.columns}
    expected = {
        "id", "topic_id", "lesson_id", "lesson_filename", "quiz_type",
        "question", "quiz_learnt", "option_a", "option_b", "option_c", "option_d",
        "correct_options", "response_to_user_option_a", "response_to_user_option_b",
        "response_to_user_option_c", "response_to_user_option_d",
        "quiz_take_away", "created_at",
    }
    assert expected.issubset(columns)


def test_quiz_log_columns():
    """QuizLog has user_answer JSON column."""
    columns = {c.name for c in QuizLog.__table__.columns}
    assert "user_answer" in columns
    assert "assessment_result" in columns


def test_topic_memory_recall_probability(db_session):
    """m(t) formula is correct."""
    import math
    mem = UserTopicMemory(
        username="test", topic_id="t1", forgetting_rate=0.3,
        last_review_quiz_count=10, review_count=1, correct_count=0,
    )
    db_session.add(mem)
    db_session.commit()

    # m(t) = exp(-0.3 * (20 - 10) / 10) = exp(-0.3)
    result = mem.recall_probability(20)
    assert abs(result - math.exp(-0.3)) < 0.001


def test_topic_memory_never_reviewed(db_session):
    """Never-reviewed returns 1.0."""
    mem = UserTopicMemory(
        username="test", topic_id="t1", forgetting_rate=0.3,
        last_review_quiz_count=None, review_count=0, correct_count=0,
    )
    db_session.add(mem)
    db_session.commit()

    assert mem.recall_probability(10) == 1.0


def test_topic_memory_update_on_correct(db_session):
    """n *= 0.7 on correct."""
    mem = UserTopicMemory(
        username="test", topic_id="t1", forgetting_rate=0.3,
        review_count=0, correct_count=0,
    )
    db_session.add(mem)
    db_session.commit()

    mem.update_on_correct(alpha=0.3)
    assert abs(mem.forgetting_rate - 0.21) < 0.001


def test_topic_memory_update_on_incorrect(db_session):
    """n *= 1.2 on incorrect, capped at 1.5."""
    mem = UserTopicMemory(
        username="test", topic_id="t1", forgetting_rate=1.4,
        review_count=0, correct_count=0,
    )
    db_session.add(mem)
    db_session.commit()

    mem.update_on_incorrect(beta=0.2)
    assert mem.forgetting_rate == 1.5  # capped


def test_lesson_memory_recall(db_session):
    """Lesson memory uses same formula."""
    import math
    mem = UserLessonMemory(
        username="test", topic_id="t1", lesson_id=1,
        forgetting_rate=0.3, last_review_quiz_count=5,
        review_count=1, correct_count=0,
    )
    db_session.add(mem)
    db_session.commit()

    result = mem.recall_probability(15)
    assert abs(result - math.exp(-0.3)) < 0.001
