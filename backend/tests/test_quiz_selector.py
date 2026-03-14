"""Tests for quiz selector — MEMORIZE-based selection."""

from unittest.mock import patch

from src.crud.crud_user import create_user
from src.crud.crud_quiz_log import create_quiz_log
from src.crud.crud_question_memory import (
    get_or_create_memory as get_or_create_qmem,
)
from src.models.quiz_question import QuizQuestion
from src.service.quiz_selector import (
    select_question_by_recall,
    select_quiz,
)


def _create_question(db, topic_id="t1", lesson_id=1, quiz_type="recall"):
    """Helper to create test quiz question."""
    q = QuizQuestion(
        topic_id=topic_id,
        lesson_id=lesson_id,
        lesson_filename="test.md",
        quiz_type=quiz_type,
        question="What?",
        quiz_learnt="Learn",
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


def _patch_topic_lookup():
    """Patch topic_lookup for select_quiz (only get_topic_for_lesson used now)."""
    return patch(
        "src.service.quiz_selector.get_topic_for_lesson",
        side_effect=lambda lid: "t1" if lid in (1, 2) else "t2" if lid == 3 else None,
    )


class TestQuestionRecallSelection:
    """Tests for question-level recall selection (Cases 2 & 3)."""

    def test_never_answered_prioritized(self, db_session):
        """Never-answered question selected over recently-correct one."""
        create_user(db_session, "testuser", "hash")
        q1 = _create_question(db_session, "t1", 1, "recall")
        q2 = _create_question(db_session, "t1", 1, "understanding")

        # Mark q1 as recently reviewed with high recall
        mem = get_or_create_qmem(db_session, "testuser", q1.id)
        mem.review_count = 3
        mem.last_review_quiz_count = 10
        mem.forgetting_rate = 0.1
        db_session.commit()
        # Create quiz logs so total count is 10
        for _ in range(10):
            create_quiz_log(db_session, "testuser", q1.id, "t1", 1, "recall")

        # q2 is never answered → recall = 0.0, should be picked
        result = select_question_by_recall(db_session, "testuser", topic_id="t1")
        assert result is not None
        assert result.id == q2.id

    def test_lowest_recall_selected(self, db_session):
        """Question with lowest m(t) selected when all reviewed."""
        create_user(db_session, "testuser", "hash")
        q1 = _create_question(db_session, "t1", 1, "recall")
        q2 = _create_question(db_session, "t1", 1, "understanding")

        # Create quiz logs so total count is 20
        for _ in range(20):
            create_quiz_log(db_session, "testuser", q1.id, "t1", 1, "recall")

        # q1: recently reviewed (high recall)
        mem1 = get_or_create_qmem(db_session, "testuser", q1.id)
        mem1.review_count = 5
        mem1.last_review_quiz_count = 19
        mem1.forgetting_rate = 0.3

        # q2: reviewed long ago (low recall)
        mem2 = get_or_create_qmem(db_session, "testuser", q2.id)
        mem2.review_count = 2
        mem2.last_review_quiz_count = 1
        mem2.forgetting_rate = 0.5
        db_session.commit()

        result = select_question_by_recall(db_session, "testuser", topic_id="t1")
        assert result is not None
        assert result.id == q2.id

    def test_exclude_ids_respected(self, db_session):
        """Excluded question IDs are not selected."""
        create_user(db_session, "testuser", "hash")
        q1 = _create_question(db_session, "t1", 1, "recall")
        q2 = _create_question(db_session, "t1", 1, "understanding")

        # Both never answered, but q1 excluded
        result = select_question_by_recall(
            db_session, "testuser", topic_id="t1", exclude_ids=[q1.id]
        )
        assert result is not None
        assert result.id == q2.id

    def test_cross_lesson_within_topic(self, db_session):
        """Questions from multiple lessons in one topic are all eligible."""
        create_user(db_session, "testuser", "hash")
        q1 = _create_question(db_session, "t1", 1, "recall")
        q2 = _create_question(db_session, "t1", 2, "recall")

        # Both never answered → both at 0.0, first by iteration wins
        result = select_question_by_recall(db_session, "testuser", topic_id="t1")
        assert result is not None
        assert result.id in {q1.id, q2.id}

    def test_all_types_eligible(self, db_session):
        """Questions from all quiz types can be selected (no rotation)."""
        create_user(db_session, "testuser", "hash")
        q_recall = _create_question(db_session, "t1", 1, "recall")
        q_understanding = _create_question(db_session, "t1", 1, "understanding")
        q_application = _create_question(db_session, "t1", 1, "application")
        q_analysis = _create_question(db_session, "t1", 1, "analysis")
        all_ids = {q_recall.id, q_understanding.id, q_application.id, q_analysis.id}

        # All never answered → all eligible
        result = select_question_by_recall(db_session, "testuser", topic_id="t1")
        assert result is not None
        assert result.id in all_ids

    def test_global_scope_no_topic_filter(self, db_session):
        """Without topic_id, questions from all topics are eligible."""
        create_user(db_session, "testuser", "hash")
        q1 = _create_question(db_session, "t1", 1, "recall")
        q2 = _create_question(db_session, "t2", 3, "recall")

        result = select_question_by_recall(db_session, "testuser")
        assert result is not None
        assert result.id in {q1.id, q2.id}

    def test_returns_none_when_all_excluded(self, db_session):
        """Returns None when all questions are excluded."""
        create_user(db_session, "testuser", "hash")
        q1 = _create_question(db_session, "t1", 1, "recall")

        result = select_question_by_recall(
            db_session, "testuser", topic_id="t1", exclude_ids=[q1.id]
        )
        assert result is None


class TestScopeResolution:
    """Tests for scope resolution in select_quiz."""

    def test_scope_lesson_id(self, db_session):
        """lesson_id uses sliding window dedup (Case 1)."""
        create_user(db_session, "testuser", "hash")
        _create_question(db_session, "t1", 1)

        with _patch_topic_lookup():
            result = select_quiz(db_session, "testuser", lesson_id=1)
        assert result is not None
        assert result.lesson_id == 1

    def test_scope_topic_id(self, db_session):
        """topic_id uses question-level recall (Case 2)."""
        create_user(db_session, "testuser", "hash")
        _create_question(db_session, "t1", 1)

        result = select_quiz(db_session, "testuser", topic_id="t1")
        assert result is not None

    def test_scope_default(self, db_session):
        """No scope uses question-level recall globally (Case 3)."""
        create_user(db_session, "testuser", "hash")
        _create_question(db_session, "t1", 1)

        result = select_quiz(db_session, "testuser")
        assert result is not None


class TestLessonScopedDedup:
    """Tests for lesson-scoped deduplication (no repeats until all seen)."""

    def test_no_repeats_in_lesson_loop(self, db_session):
        """All questions appear before any repeat in a lesson-scoped loop."""
        create_user(db_session, "testuser", "hash")
        q1 = _create_question(db_session, "t1", 1, "recall")
        q2 = _create_question(db_session, "t1", 1, "understanding")
        q3 = _create_question(db_session, "t1", 1, "application")
        q4 = _create_question(db_session, "t1", 1, "analysis")
        all_ids = {q1.id, q2.id, q3.id, q4.id}

        seen_ids = set()
        with _patch_topic_lookup():
            for _ in range(4):
                result = select_quiz(db_session, "testuser", lesson_id=1)
                assert result is not None
                assert result.id not in seen_ids, f"Question {result.id} repeated before all seen"
                seen_ids.add(result.id)
                create_quiz_log(db_session, "testuser", result.id, "t1", 1, result.quiz_type)

        assert seen_ids == all_ids

    def test_no_repeats_across_multiple_loops(self, db_session):
        """Sliding window ensures no repeats even across loop boundaries."""
        create_user(db_session, "testuser", "hash")
        _create_question(db_session, "t1", 1, "recall")
        _create_question(db_session, "t1", 1, "understanding")
        _create_question(db_session, "t1", 1, "application")
        _create_question(db_session, "t1", 1, "analysis")

        with _patch_topic_lookup():
            last_ids = []
            for i in range(12):
                result = select_quiz(db_session, "testuser", lesson_id=1)
                assert result is not None
                assert (
                    result.id not in last_ids[-3:]
                ), f"Question {result.id} repeated within window at position {i}"
                last_ids.append(result.id)
                create_quiz_log(db_session, "testuser", result.id, "t1", 1, result.quiz_type)

    def test_lesson_loop_continues_after_all_seen(self, db_session):
        """After all questions seen, questions are still available (sliding window)."""
        create_user(db_session, "testuser", "hash")
        _create_question(db_session, "t1", 1, "recall")
        _create_question(db_session, "t1", 1, "understanding")

        with _patch_topic_lookup():
            for _ in range(2):
                result = select_quiz(db_session, "testuser", lesson_id=1)
                assert result is not None
                create_quiz_log(db_session, "testuser", result.id, "t1", 1, result.quiz_type)

            result = select_quiz(db_session, "testuser", lesson_id=1)
            assert result is not None


class TestTopicScopedLoop:
    """Tests for topic-scoped loop with sliding window (Case 2)."""

    def test_loop_size_capped_at_10(self, db_session):
        """Loop window is capped at 10 even with more questions."""
        create_user(db_session, "testuser", "hash")
        # Create 12 questions
        [_create_question(db_session, "t1", 1, "recall") for _ in range(12)]

        # Serve 10 questions (loop_size = min(10, 12) = 10, window = 9)
        seen = set()
        for i in range(10):
            result = select_quiz(db_session, "testuser", topic_id="t1")
            assert result is not None
            seen.add(result.id)
            create_quiz_log(db_session, "testuser", result.id, "t1", 1, result.quiz_type)

        # After 10, next question should still be available (window only excludes 9)
        result = select_quiz(db_session, "testuser", topic_id="t1")
        assert result is not None

    def test_sliding_window_prevents_immediate_repeat(self, db_session):
        """Questions in the sliding window are not re-served."""
        create_user(db_session, "testuser", "hash")
        q1 = _create_question(db_session, "t1", 1, "recall")
        q2 = _create_question(db_session, "t1", 1, "understanding")
        q3 = _create_question(db_session, "t1", 1, "application")

        # Serve q1 and q2 (window size = min(10,3)-1 = 2)
        for q in [q1, q2]:
            create_quiz_log(db_session, "testuser", q.id, "t1", 1, q.quiz_type)

        # Next should be q3 (the only one not in the window)
        result = select_quiz(db_session, "testuser", topic_id="t1")
        assert result is not None
        assert result.id == q3.id
