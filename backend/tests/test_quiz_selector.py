"""Tests for quiz selector — MEMORIZE-based selection."""

from unittest.mock import patch

from src.crud.crud_user import create_user
from src.crud.crud_quiz_log import create_quiz_log
from src.crud.crud_topic_memory import (
    get_or_create_memory as get_or_create_topic,
    update_memory_on_quiz_result,
)
from src.crud.crud_lesson_memory import get_or_create_memory as get_or_create_lesson
from src.models.quiz_question import QuizQuestion
from src.service.quiz_selector import (
    select_topic_for_quiz,
    select_lesson_for_quiz,
    select_quiz_type,
    select_quiz,
)


def _create_question(db, topic_id="t1", lesson_id=1, quiz_type="recall"):
    """Helper to create test quiz question."""
    q = QuizQuestion(
        topic_id=topic_id, lesson_id=lesson_id, lesson_filename="test.md",
        quiz_type=quiz_type, question="What?", quiz_learnt="Learn",
        option_a="A", option_b="B", option_c="C", option_d="D",
        correct_options=["B"],
        response_to_user_option_a="eA", response_to_user_option_b="eB",
        response_to_user_option_c="eC", response_to_user_option_d="eD",
        quiz_take_away="TK",
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


MOCK_TOPICS = {
    "t1": {"id": "t1", "name": "Topic 1", "lesson_ids": [1, 2]},
    "t2": {"id": "t2", "name": "Topic 2", "lesson_ids": [3]},
}


def _patch_topic_lookup():
    """Patch topic_lookup to use MOCK_TOPICS."""
    return patch.multiple(
        "src.service.quiz_selector",
        get_all_topic_ids=lambda: list(MOCK_TOPICS.keys()),
        get_lessons_for_topic=lambda tid: MOCK_TOPICS.get(tid, {}).get("lesson_ids", []),
        get_topic_for_lesson=lambda lid: next(
            (tid for tid, t in MOCK_TOPICS.items() if lid in t["lesson_ids"]), None
        ),
    )


class TestTopicSelection:
    """Tests for topic selection."""

    def test_select_topic_never_reviewed_first(self, db_session):
        """Never-reviewed topics get m(t)=0.0 and are selected first."""
        create_user(db_session, "testuser", "hash")
        # t1 has been reviewed, t2 has not
        topic_mem = get_or_create_topic(db_session, "testuser", "t1")
        topic_mem.last_review_quiz_count = 5
        db_session.commit()

        with _patch_topic_lookup():
            result = select_topic_for_quiz(db_session, "testuser")
        assert result == "t2"

    def test_select_topic_lowest_recall(self, db_session):
        """Picks topic with lowest m(t) when all reviewed."""
        create_user(db_session, "testuser", "hash")
        # Create quiz logs so total count is 10
        q = _create_question(db_session, "t1", 1)
        for _ in range(10):
            create_quiz_log(db_session, "testuser", q.id, "t1", 1, "recall")
        # t1: recently reviewed (high recall) — reviewed at quiz 9
        mem1 = get_or_create_topic(db_session, "testuser", "t1")
        mem1.last_review_quiz_count = 9
        # t2: reviewed long ago (low recall) — reviewed at quiz 1
        mem2 = get_or_create_topic(db_session, "testuser", "t2")
        mem2.last_review_quiz_count = 1
        mem2.forgetting_rate = 0.5
        db_session.commit()

        with _patch_topic_lookup():
            result = select_topic_for_quiz(db_session, "testuser")
        assert result == "t2"


class TestLessonSelection:
    """Tests for lesson selection."""

    def test_select_lesson_never_reviewed_first(self, db_session):
        """Never-reviewed lessons get m(t)=0.0."""
        create_user(db_session, "testuser", "hash")
        _create_question(db_session, "t1", 1)
        _create_question(db_session, "t1", 2)
        # Lesson 1 reviewed, lesson 2 never
        get_or_create_lesson(db_session, "testuser", "t1", 1)
        mem = get_or_create_lesson(db_session, "testuser", "t1", 1)
        mem.last_review_quiz_count = 5
        db_session.commit()

        with _patch_topic_lookup():
            result = select_lesson_for_quiz(db_session, "testuser", "t1")
        assert result == 2

    def test_select_lesson_lowest_recall(self, db_session):
        """Picks lesson with lowest m(t)."""
        create_user(db_session, "testuser", "hash")
        q1 = _create_question(db_session, "t1", 1)
        _create_question(db_session, "t1", 2)
        # Create quiz logs so total count is 10
        for _ in range(10):
            create_quiz_log(db_session, "testuser", q1.id, "t1", 1, "recall")
        # Lesson 1: recent (high recall) — reviewed at quiz 9
        mem1 = get_or_create_lesson(db_session, "testuser", "t1", 1)
        mem1.last_review_quiz_count = 9
        # Lesson 2: old (low recall) — reviewed at quiz 1
        mem2 = get_or_create_lesson(db_session, "testuser", "t1", 2)
        mem2.last_review_quiz_count = 1
        mem2.forgetting_rate = 0.5
        db_session.commit()

        with _patch_topic_lookup():
            result = select_lesson_for_quiz(db_session, "testuser", "t1")
        assert result == 2


class TestScopeResolution:
    """Tests for scope resolution in select_quiz."""

    def test_scope_lesson_id(self, db_session):
        """lesson_id skips both selectors."""
        create_user(db_session, "testuser", "hash")
        q = _create_question(db_session, "t1", 1)

        with _patch_topic_lookup():
            result = select_quiz(db_session, "testuser", lesson_id=1)
        assert result is not None
        assert result.lesson_id == 1

    def test_scope_topic_id(self, db_session):
        """topic_id skips topic selector."""
        create_user(db_session, "testuser", "hash")
        _create_question(db_session, "t1", 1)

        with _patch_topic_lookup():
            result = select_quiz(db_session, "testuser", topic_id="t1")
        assert result is not None

    def test_scope_default(self, db_session):
        """No scope uses both selectors."""
        create_user(db_session, "testuser", "hash")
        _create_question(db_session, "t1", 1)

        with _patch_topic_lookup():
            result = select_quiz(db_session, "testuser")
        assert result is not None


class TestQuizTypeRotation:
    """Tests for quiz type rotation."""

    def test_rotation_skips_recent(self, db_session):
        """Skips 3 most recently used types."""
        create_user(db_session, "testuser", "hash")
        q = _create_question(db_session, "t1", 1, "recall")
        # Create logs with 3 recent types
        for qt in ["recall", "understanding", "application"]:
            q2 = _create_question(db_session, "t1", 1, qt)
            create_quiz_log(db_session, "testuser", q2.id, "t1", 1, qt)

        result = select_quiz_type(db_session, "testuser")
        assert result == "analysis"

    def test_rotation_fewer_than_3_history(self, db_session):
        """With limited history, excludes fewer types."""
        create_user(db_session, "testuser", "hash")
        q = _create_question(db_session, "t1", 1, "recall")
        create_quiz_log(db_session, "testuser", q.id, "t1", 1, "recall")

        result = select_quiz_type(db_session, "testuser")
        assert result != "recall"
