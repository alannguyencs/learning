"""Tests for recall dashboard Pydantic schemas."""

from datetime import datetime

from src.schemas.recall_dashboard import (
    LessonRecallItem,
    RecallMapResponse,
    TopicMatrixResponse,
    TopicMatrixRow,
    TopicQuizAttempt,
    TopicRecallItem,
)


def test_lesson_recall_item():
    """All fields present and typed."""
    item = LessonRecallItem(
        lesson_id=1,
        lesson_name="Intro",
        recall_probability=0.72,
        forgetting_rate=0.21,
        last_review_at=datetime(2025, 1, 1),
        review_count=5,
        correct_count=4,
    )
    assert item.lesson_id == 1
    assert item.lesson_name == "Intro"
    assert item.recall_probability == 0.72
    assert item.forgetting_rate == 0.21
    assert item.review_count == 5
    assert item.correct_count == 4


def test_lesson_recall_item_no_review():
    """last_review_at can be None."""
    item = LessonRecallItem(
        lesson_id=2,
        lesson_name="Basics",
        recall_probability=1.0,
        forgetting_rate=0.3,
        last_review_at=None,
        review_count=0,
        correct_count=0,
    )
    assert item.last_review_at is None


def test_topic_recall_item_with_lessons():
    """Nested lessons list."""
    lesson = LessonRecallItem(
        lesson_id=1, lesson_name="L1", recall_probability=0.8,
        forgetting_rate=0.2, last_review_at=None, review_count=3, correct_count=2,
    )
    topic = TopicRecallItem(
        topic_id="t1", topic_name="Topic One", lesson_count=1,
        recall_probability=0.85, forgetting_rate=0.15,
        last_review_at=datetime(2025, 1, 1), review_count=10, correct_count=8,
        lessons=[lesson],
    )
    assert topic.topic_id == "t1"
    assert len(topic.lessons) == 1
    assert topic.lessons[0].lesson_id == 1


def test_recall_map_response():
    """Includes lessons_at_risk."""
    resp = RecallMapResponse(
        topics=[], global_recall=0.78, topics_at_risk=2, lessons_at_risk=5,
    )
    assert resp.global_recall == 0.78
    assert resp.topics_at_risk == 2
    assert resp.lessons_at_risk == 5


def test_topic_quiz_attempt():
    """Quiz attempt cell fields."""
    attempt = TopicQuizAttempt(
        quiz_id=1, result="correct",
        asked_at=datetime(2025, 1, 1), column_index=3, lesson_name="Lesson A",
    )
    assert attempt.quiz_id == 1
    assert attempt.result == "correct"
    assert attempt.column_index == 3
    assert attempt.lesson_name == "Lesson A"


def test_topic_matrix_row():
    """Row with quiz attempts."""
    attempt = TopicQuizAttempt(
        quiz_id=1, result="incorrect",
        asked_at=datetime(2025, 1, 1), column_index=1, lesson_name="L1",
    )
    row = TopicMatrixRow(
        topic_id="t1", topic_name="Topic One", lesson_count=3,
        last_quiz_at=datetime(2025, 1, 1), quizzes=[attempt],
    )
    assert len(row.quizzes) == 1
    assert row.topic_name == "Topic One"


def test_topic_matrix_response():
    """Topics with quiz attempts and max count."""
    resp = TopicMatrixResponse(topics=[], max_quiz_count=47)
    assert resp.max_quiz_count == 47
    assert resp.topics == []
