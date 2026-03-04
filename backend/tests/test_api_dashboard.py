"""Tests for recall dashboard API endpoints."""

from unittest.mock import patch

from passlib.context import CryptContext

from src.crud.crud_user import create_user
from src.crud.crud_quiz_log import create_quiz_log
from src.crud.crud_topic_memory import get_or_create_memory as get_or_create_topic
from src.crud.crud_lesson_memory import get_or_create_memory as get_or_create_lesson
from src.models.quiz_question import QuizQuestion

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MOCK_TOPICS = {
    "t1": {"name": "Topic One", "lessons": [1, 2]},
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
    return {1: "Lesson A", 2: "Lesson B"}.get(lid, f"Lesson {lid}")


def _login(client, db_session, username="testuser"):
    hashed = bcrypt_context.hash("testpass")
    create_user(db_session, username, hashed)
    client.post("/api/login/", json={"username": username, "password": "testpass"})
    return username


def _create_question(db, topic_id="t1", lesson_id=1):
    q = QuizQuestion(
        topic_id=topic_id, lesson_id=lesson_id, lesson_filename="test.md",
        quiz_type="recall", question="Q?", quiz_learnt="Learn",
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


_LOOKUP_PATCHES = {
    "src.service.recall_service.get_all_topic_ids": _mock_get_all_topic_ids,
    "src.service.recall_service.get_topic_name": _mock_get_topic_name,
    "src.service.recall_service.get_lessons_for_topic": _mock_get_lessons_for_topic,
    "src.service.recall_service.get_lesson_count": _mock_get_lesson_count,
    "src.service.recall_service.get_lesson_name": _mock_get_lesson_name,
}


def _start_patches():
    patches = []
    for target, replacement in _LOOKUP_PATCHES.items():
        p = patch(target, side_effect=replacement)
        p.start()
        patches.append(p)
    return patches


def _stop_patches(patches):
    for p in patches:
        p.stop()


class TestDashboardEndpoints:
    """Tests for recall dashboard API endpoints."""

    def test_recall_map_requires_auth(self, client):
        """Returns 401 without session."""
        response = client.get("/api/quiz/recall-map")
        assert response.status_code == 401

    def test_topic_matrix_requires_auth(self, client):
        """Returns 401 without session."""
        response = client.get("/api/quiz/topic-matrix")
        assert response.status_code == 401

    def test_recall_map_endpoint(self, client, db_session):
        """Returns 200 with correct schema."""
        patches = _start_patches()
        try:
            _login(client, db_session)
            response = client.get("/api/quiz/recall-map")
            assert response.status_code == 200
            data = response.json()
            assert "topics" in data
            assert "global_recall" in data
            assert "topics_at_risk" in data
            assert "lessons_at_risk" in data
        finally:
            _stop_patches(patches)

    def test_recall_map_nested_lessons(self, client, db_session):
        """Response includes lesson-level data."""
        patches = _start_patches()
        try:
            _login(client, db_session)
            response = client.get("/api/quiz/recall-map")
            assert response.status_code == 200
            data = response.json()
            assert len(data["topics"]) > 0
            topic = data["topics"][0]
            assert "lessons" in topic
            assert len(topic["lessons"]) == 2
            assert topic["lessons"][0]["lesson_name"] == "Lesson A"
        finally:
            _stop_patches(patches)

    def test_topic_matrix_endpoint(self, client, db_session):
        """Returns 200 with correct schema."""
        patches = _start_patches()
        try:
            username = _login(client, db_session)
            q = _create_question(db_session)
            create_quiz_log(db_session, username, q.id, "t1", 1, "recall")

            response = client.get("/api/quiz/topic-matrix")
            assert response.status_code == 200
            data = response.json()
            assert "topics" in data
            assert "max_quiz_count" in data
            assert data["max_quiz_count"] == 1
        finally:
            _stop_patches(patches)
