"""Tests for RecallService — recall map and topic matrix."""

from datetime import datetime
from unittest.mock import patch

from src.crud.crud_quiz_log import create_quiz_log, record_quiz_answer
from src.crud.crud_topic_memory import get_or_create_memory as get_or_create_topic
from src.crud.crud_lesson_memory import get_or_create_memory as get_or_create_lesson
from src.models.quiz_question import QuizQuestion
from src.service.recall_service import RecallService


def _create_question(db, topic_id="t1", lesson_id=1, quiz_type="recall"):
    q = QuizQuestion(
        topic_id=topic_id,
        lesson_id=lesson_id,
        lesson_filename="test.md",
        quiz_type=quiz_type,
        question="Q?",
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


# Patch topic_lookup functions to return controlled data
MOCK_TOPICS = {
    "t1": {"name": "Topic One", "lessons": [1, 2]},
    "t2": {"name": "Topic Two", "lessons": [3]},
}


def _mock_get_all_topic_ids():
    return list(MOCK_TOPICS.keys())


def _mock_get_topic_name(tid):
    return MOCK_TOPICS.get(tid, {}).get("name", tid)


def _mock_get_lessons_for_topic(tid):
    return MOCK_TOPICS.get(tid, {}).get("lessons", [])


def _mock_get_lesson_count(tid):
    return len(MOCK_TOPICS.get(tid, {}).get("lessons", []))


def _mock_get_lesson_name(lid):
    names = {1: "Lesson A", 2: "Lesson B", 3: "Lesson C"}
    return names.get(lid, f"Lesson {lid}")


_LOOKUP_PATCHES = {
    "src.service.recall_service.get_all_topic_ids": _mock_get_all_topic_ids,
    "src.service.recall_service.get_topic_name": _mock_get_topic_name,
    "src.service.recall_service.get_lessons_for_topic": _mock_get_lessons_for_topic,
    "src.service.recall_service.get_lesson_count": _mock_get_lesson_count,
    "src.service.recall_service.get_lesson_name": _mock_get_lesson_name,
}


def _apply_patches():
    """Return a list of started mock patches."""
    patches = []
    for target, replacement in _LOOKUP_PATCHES.items():
        p = patch(target, side_effect=replacement)
        p.start()
        patches.append(p)
    return patches


def _stop_patches(patches):
    for p in patches:
        p.stop()


class TestRecallMap:
    """Tests for RecallService.get_recall_map."""

    def test_recall_map_no_quizzes(self, db_session):
        """All topics at m(t)=1.0, global_recall=1.0 when no quiz data."""
        patches = _apply_patches()
        try:
            result = RecallService.get_recall_map(db_session, "user1")
            assert result.global_recall == 1.0
            assert result.global_accuracy == 0.0
            assert result.topics_at_risk == 0
            assert result.lessons_at_risk == 0
            assert len(result.topics) == 2
            for topic in result.topics:
                assert topic.recall_probability == 1.0
        finally:
            _stop_patches(patches)

    def test_recall_map_with_topic_data(self, db_session):
        """Correct topic m(t) computation with memory records.

        Accuracy uses latest answer per unique question:
        review_count = K (total questions), correct_count = latest correct.
        """
        patches = _apply_patches()
        try:
            # Create topic memory with some reviews
            tm = get_or_create_topic(db_session, "user1", "t1")
            tm.review_count = 5
            tm.correct_count = 4
            tm.last_review_quiz_count = 1
            tm.last_review_at = datetime(2025, 1, 1)
            db_session.commit()

            # Create 1 question for lesson 1 and answer it correctly
            q = _create_question(db_session, "t1", 1)
            log = create_quiz_log(db_session, "user1", q.id, "t1", 1, "recall")
            record_quiz_answer(db_session, log.id, ["B"], "correct")
            # Extra logs for elapsed count
            for _ in range(4):
                create_quiz_log(db_session, "user1", q.id, "t1", 1, "recall")

            result = RecallService.get_recall_map(db_session, "user1")
            t1_data = next(t for t in result.topics if t.topic_id == "t1")
            # review_count = K across all lessons (1 question in lesson 1, 0 in lesson 2)
            assert t1_data.review_count == 1
            assert t1_data.correct_count == 1
            assert t1_data.recall_probability < 1.0  # has decayed (elapsed=4)
        finally:
            _stop_patches(patches)

    def test_recall_map_with_lesson_data(self, db_session):
        """Correct lesson accuracy: latest answer per unique question.

        review_count = K (total questions), correct_count = latest correct.
        """
        patches = _apply_patches()
        try:
            lm = get_or_create_lesson(db_session, "user1", "t1", 1)
            lm.review_count = 3
            lm.correct_count = 2
            lm.last_review_quiz_count = 1
            lm.last_review_at = datetime(2025, 1, 1)
            db_session.commit()

            # Create 1 question for lesson 1, answer wrong then correct
            q = _create_question(db_session, "t1", 1)
            log1 = create_quiz_log(db_session, "user1", q.id, "t1", 1, "recall")
            record_quiz_answer(db_session, log1.id, ["A"], "incorrect")
            log2 = create_quiz_log(db_session, "user1", q.id, "t1", 1, "recall")
            record_quiz_answer(db_session, log2.id, ["B"], "correct")
            # Extra logs for elapsed count
            for _ in range(3):
                create_quiz_log(db_session, "user1", q.id, "t1", 1, "recall")

            result = RecallService.get_recall_map(db_session, "user1")
            t1_data = next(t for t in result.topics if t.topic_id == "t1")
            l1_data = next(l for l in t1_data.lessons if l.lesson_id == 1)
            # review_count = K = 1 (only 1 question), correct_count = 1 (latest answer is correct)
            assert l1_data.review_count == 1
            assert l1_data.correct_count == 1
            assert l1_data.recall_probability < 1.0  # elapsed > 0
        finally:
            _stop_patches(patches)

    def test_topics_at_risk_count(self, db_session):
        """Counts topics with m(t) < 0.5."""
        patches = _apply_patches()
        try:
            # Create topic with high forgetting rate and many quizzes elapsed
            tm = get_or_create_topic(db_session, "user1", "t1")
            tm.review_count = 1
            tm.forgetting_rate = 1.5
            tm.last_review_quiz_count = 1
            tm.last_review_at = datetime(2025, 1, 1)
            db_session.commit()

            # Create many quiz logs so elapsed is large
            q = _create_question(db_session, "t1", 1)
            for _ in range(20):
                create_quiz_log(db_session, "user1", q.id, "t1", 1, "recall")

            result = RecallService.get_recall_map(db_session, "user1")
            assert result.topics_at_risk >= 1
        finally:
            _stop_patches(patches)

    def test_lessons_at_risk_count(self, db_session):
        """Counts lessons with m(t) < 0.5."""
        patches = _apply_patches()
        try:
            lm = get_or_create_lesson(db_session, "user1", "t1", 1)
            lm.review_count = 1
            lm.forgetting_rate = 1.5
            lm.last_review_quiz_count = 1
            lm.last_review_at = datetime(2025, 1, 1)
            db_session.commit()

            q = _create_question(db_session, "t1", 1)
            for _ in range(20):
                create_quiz_log(db_session, "user1", q.id, "t1", 1, "recall")

            result = RecallService.get_recall_map(db_session, "user1")
            assert result.lessons_at_risk >= 1
        finally:
            _stop_patches(patches)

    def test_global_recall_mean(self, db_session):
        """Global recall is mean of topic m(t) values."""
        patches = _apply_patches()
        try:
            result = RecallService.get_recall_map(db_session, "user1")
            # Both topics at 1.0 → mean = 1.0
            assert result.global_recall == 1.0
        finally:
            _stop_patches(patches)

    def test_never_reviewed_shows_1_0(self, db_session):
        """Never-reviewed topics/lessons show m(t)=1.0."""
        patches = _apply_patches()
        try:
            result = RecallService.get_recall_map(db_session, "user1")
            for topic in result.topics:
                assert topic.recall_probability == 1.0
                for lesson in topic.lessons:
                    assert lesson.recall_probability == 1.0
        finally:
            _stop_patches(patches)


class TestTopicMatrix:
    """Tests for RecallService.get_topic_matrix."""

    def test_matrix_chronological_order(self, db_session):
        """column_index matches created_at order."""
        patches = _apply_patches()
        try:
            q = _create_question(db_session, "t1", 1)
            create_quiz_log(db_session, "user1", q.id, "t1", 1, "recall")
            create_quiz_log(db_session, "user1", q.id, "t1", 1, "recall")

            result = RecallService.get_topic_matrix(db_session, "user1")
            t1_row = next(r for r in result.topics if r.topic_id == "t1")
            indices = [quiz.column_index for quiz in t1_row.quizzes]
            assert indices == [1, 2]
        finally:
            _stop_patches(patches)

    def test_matrix_groups_by_topic(self, db_session):
        """Quizzes grouped into correct topic rows."""
        patches = _apply_patches()
        try:
            q1 = _create_question(db_session, "t1", 1)
            q2 = _create_question(db_session, "t2", 3)
            create_quiz_log(db_session, "user1", q1.id, "t1", 1, "recall")
            create_quiz_log(db_session, "user1", q2.id, "t2", 3, "recall")

            result = RecallService.get_topic_matrix(db_session, "user1")
            t1_row = next(r for r in result.topics if r.topic_id == "t1")
            t2_row = next(r for r in result.topics if r.topic_id == "t2")
            assert len(t1_row.quizzes) == 1
            assert len(t2_row.quizzes) == 1
        finally:
            _stop_patches(patches)

    def test_matrix_lesson_name_tooltip(self, db_session):
        """Each cell includes lesson_name."""
        patches = _apply_patches()
        try:
            q = _create_question(db_session, "t1", 1)
            create_quiz_log(db_session, "user1", q.id, "t1", 1, "recall")

            result = RecallService.get_topic_matrix(db_session, "user1")
            t1_row = next(r for r in result.topics if r.topic_id == "t1")
            assert t1_row.quizzes[0].lesson_name == "Lesson A"
        finally:
            _stop_patches(patches)

    def test_matrix_empty_user(self, db_session):
        """Returns empty topics with max_quiz_count=0."""
        patches = _apply_patches()
        try:
            result = RecallService.get_topic_matrix(db_session, "user1")
            assert result.max_quiz_count == 0
            for row in result.topics:
                assert len(row.quizzes) == 0
        finally:
            _stop_patches(patches)
