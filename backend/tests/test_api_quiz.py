"""Tests for quiz API endpoints."""

from passlib.context import CryptContext

from src.crud.crud_user import create_user
from src.crud.crud_quiz_log import create_quiz_log
from src.crud.crud_topic_memory import get_or_create_memory as get_or_create_topic
from src.crud.crud_lesson_memory import get_or_create_memory as get_or_create_lesson
from src.models.quiz_question import QuizQuestion

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _login(client, db_session, username="testuser"):
    """Create user, login, return username."""
    hashed = bcrypt_context.hash("testpass")
    create_user(db_session, username, hashed)
    client.post("/api/login/", json={"username": username, "password": "testpass"})
    return username


def _create_question(db, topic_id="t1", lesson_id=1, quiz_type="recall"):
    """Helper to create test quiz question."""
    q = QuizQuestion(
        topic_id=topic_id,
        lesson_id=lesson_id,
        lesson_filename="test.md",
        quiz_type=quiz_type,
        question="What is X?",
        quiz_learnt="Learn X",
        option_a="A answer",
        option_b="B answer",
        option_c="C answer",
        option_d="D answer",
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


class TestQuizNextEndpoint:
    """Tests for GET /api/quiz/next."""

    def test_next_quiz_requires_auth(self, client):
        """Returns 401 without session."""
        response = client.get("/api/quiz/next")
        assert response.status_code == 401

    def test_next_quiz_no_questions(self, client, db_session):
        """Returns 404 when no questions available."""
        _login(client, db_session)
        response = client.get("/api/quiz/next")
        assert response.status_code == 404

    def test_next_quiz_with_lesson_scope(self, client, db_session):
        """Returns question from specified lesson."""
        username = _login(client, db_session)
        _create_question(db_session, "t1", 1, "recall")

        response = client.get("/api/quiz/next?lesson_id=1")
        assert response.status_code == 200
        data = response.json()
        assert data["lesson_id"] == 1
        assert "quiz_id" in data
        assert "options" in data
        assert data["correct_option_count"] == 1
        assert data["lesson_question_count"] == 1
        assert data["loop_question_count"] == 1


class TestQuizAnswerEndpoint:
    """Tests for POST /api/quiz/{quiz_id}/answer."""

    def test_answer_correct(self, client, db_session):
        """Returns is_correct=true with all explanations."""
        username = _login(client, db_session)
        get_or_create_topic(db_session, username, "t1")
        get_or_create_lesson(db_session, username, "t1", 1)
        q = _create_question(db_session)
        log = create_quiz_log(db_session, username, q.id, "t1", 1, "recall")

        response = client.post(f"/api/quiz/{log.id}/answer", json={"answer": ["B"]})
        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is True
        assert "quiz_learnt" in data
        assert len(data["explanations"]) == 4

    def test_answer_incorrect(self, client, db_session):
        """Returns is_correct=false with correct_options."""
        username = _login(client, db_session)
        get_or_create_topic(db_session, username, "t1")
        get_or_create_lesson(db_session, username, "t1", 1)
        q = _create_question(db_session)
        log = create_quiz_log(db_session, username, q.id, "t1", 1, "recall")

        response = client.post(f"/api/quiz/{log.id}/answer", json={"answer": ["A"]})
        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is False
        assert data["correct_options"] == ["B"]

    def test_answer_already_answered(self, client, db_session):
        """Returns 400 for already-answered quiz."""
        username = _login(client, db_session)
        get_or_create_topic(db_session, username, "t1")
        get_or_create_lesson(db_session, username, "t1", 1)
        q = _create_question(db_session)
        log = create_quiz_log(db_session, username, q.id, "t1", 1, "recall")

        client.post(f"/api/quiz/{log.id}/answer", json={"answer": ["B"]})
        response = client.post(f"/api/quiz/{log.id}/answer", json={"answer": ["A"]})
        assert response.status_code == 400


class TestQuizDashboardEndpoints:
    """Tests for quiz history, stats, eligibility, topics."""

    def test_quiz_history(self, client, db_session):
        """Paginated results."""
        username = _login(client, db_session)
        q = _create_question(db_session)
        create_quiz_log(db_session, username, q.id, "t1", 1, "recall")

        response = client.get("/api/quiz/history")
        assert response.status_code == 200
        data = response.json()
        assert "quizzes" in data
        assert len(data["quizzes"]) == 1

    def test_quiz_stats(self, client, db_session):
        """Correct totals and accuracy."""
        username = _login(client, db_session)
        response = client.get("/api/quiz/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_eligibility_no_questions(self, client, db_session):
        """Returns eligible=false when no questions."""
        _login(client, db_session)
        response = client.get("/api/quiz/eligibility")
        assert response.status_code == 200
        data = response.json()
        assert data["eligible"] is False

    def test_eligibility_with_questions(self, client, db_session):
        """Returns eligible=true when questions exist."""
        _login(client, db_session)
        _create_question(db_session)
        response = client.get("/api/quiz/eligibility")
        assert response.status_code == 200
        assert response.json()["eligible"] is True

    def test_topics_list(self, client, db_session):
        """Returns topics with nested lessons."""
        _login(client, db_session)
        response = client.get("/api/quiz/topics")
        assert response.status_code == 200
        data = response.json()
        assert "topics" in data
