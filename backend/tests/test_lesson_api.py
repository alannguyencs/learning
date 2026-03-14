"""Tests for lesson API endpoints."""

from passlib.context import CryptContext

from src.crud.crud_user import create_user

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _login(client, db_session, username="testuser"):
    """Create user, login via cookie, return username."""
    hashed = bcrypt_context.hash("testpass")
    create_user(db_session, username, hashed)
    client.post("/api/login/", json={"username": username, "password": "testpass"})
    return username


# --- POST /api/lessons ---


def test_create_lesson_required_fields(client, db_session):
    """Create a lesson with only required fields."""
    _login(client, db_session)
    response = client.post(
        "/api/lessons",
        json={"topic": "math", "title": "Algebra Basics"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["topic"] == "math"
    assert data["title"] == "Algebra Basics"
    assert data["published_date"] is None
    assert "id" in data
    assert "created_at" in data


def test_create_lesson_all_fields(client, db_session):
    """Create a lesson with all optional fields."""
    _login(client, db_session)
    response = client.post(
        "/api/lessons",
        json={
            "topic": "science",
            "title": "Photosynthesis",
            "published_date": "2026-03-01",
            "content": "# Photosynthesis\n\nPlants convert light...",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["topic"] == "science"
    assert data["title"] == "Photosynthesis"
    assert data["published_date"] == "2026-03-01"


def test_create_lesson_missing_topic(client, db_session):
    """POST with missing topic returns 422."""
    _login(client, db_session)
    response = client.post(
        "/api/lessons",
        json={"title": "No Topic"},
    )
    assert response.status_code == 422


def test_create_lesson_missing_title(client, db_session):
    """POST with missing title returns 422."""
    _login(client, db_session)
    response = client.post(
        "/api/lessons",
        json={"topic": "math"},
    )
    assert response.status_code == 422


def test_create_lesson_unauthenticated(client):
    """POST without auth returns 401."""
    response = client.post(
        "/api/lessons",
        json={"topic": "math", "title": "Algebra"},
    )
    assert response.status_code == 401


# --- GET /api/lessons ---


def test_list_lessons(client, db_session):
    """List all lessons."""
    _login(client, db_session)

    client.post("/api/lessons", json={"topic": "math", "title": "Algebra"})
    client.post("/api/lessons", json={"topic": "science", "title": "Physics"})

    response = client.get("/api/lessons")
    assert response.status_code == 200
    data = response.json()
    assert len(data["lessons"]) == 2


def test_list_lessons_filter_by_topic(client, db_session):
    """List lessons filtered by topic."""
    _login(client, db_session)

    client.post("/api/lessons", json={"topic": "math", "title": "Algebra"})
    client.post("/api/lessons", json={"topic": "science", "title": "Physics"})

    response = client.get("/api/lessons?topic=math")
    assert response.status_code == 200
    data = response.json()
    assert len(data["lessons"]) == 1
    assert data["lessons"][0]["topic"] == "math"


def test_list_lessons_empty(client, db_session):
    """List lessons when none exist."""
    _login(client, db_session)
    response = client.get("/api/lessons")
    assert response.status_code == 200
    assert response.json()["lessons"] == []


# --- GET /api/lessons/{lesson_id} ---


def test_get_lesson_detail(client, db_session):
    """Get single lesson includes content."""
    _login(client, db_session)

    create_resp = client.post(
        "/api/lessons",
        json={
            "topic": "math",
            "title": "Algebra",
            "content": "# Algebra\n\nSolving equations...",
        },
    )
    lesson_id = create_resp.json()["id"]

    response = client.get(f"/api/lessons/{lesson_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == lesson_id
    assert data["content"] == "# Algebra\n\nSolving equations..."


def test_get_lesson_not_found(client, db_session):
    """GET non-existent lesson returns 404."""
    _login(client, db_session)
    response = client.get("/api/lessons/9999")
    assert response.status_code == 404


# --- PUT /api/lessons/{lesson_id} ---


def test_update_lesson(client, db_session):
    """Update lesson fields."""
    _login(client, db_session)

    create_resp = client.post(
        "/api/lessons",
        json={"topic": "math", "title": "Algebra"},
    )
    lesson_id = create_resp.json()["id"]

    response = client.put(
        f"/api/lessons/{lesson_id}",
        json={"title": "Advanced Algebra", "content": "# Updated"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Advanced Algebra"

    # Verify content was saved
    detail = client.get(f"/api/lessons/{lesson_id}").json()
    assert detail["content"] == "# Updated"


def test_update_lesson_not_found(client, db_session):
    """PUT non-existent lesson returns 404."""
    _login(client, db_session)
    response = client.put(
        "/api/lessons/9999",
        json={"title": "Nope"},
    )
    assert response.status_code == 404


def test_update_lesson_no_fields(client, db_session):
    """PUT with empty body returns 400."""
    _login(client, db_session)

    create_resp = client.post(
        "/api/lessons",
        json={"topic": "math", "title": "Algebra"},
    )
    lesson_id = create_resp.json()["id"]

    response = client.put(f"/api/lessons/{lesson_id}", json={})
    assert response.status_code == 400


# --- Quiz upload validates lesson_id ---


def test_quiz_upload_rejects_missing_lesson(client, db_session):
    """Upload quiz questions with non-existent lesson_id returns 400."""
    _login(client, db_session)
    response = client.post(
        "/api/quiz/questions",
        json=[
            {
                "topic_id": "math",
                "lesson_id": 9999,
                "lesson_filename": "test.md",
                "topic_name": "Math",
                "lesson_name": "Test",
                "quiz_type": "recall",
                "question": "What is 1+1?",
                "quiz_learnt": "Basic addition",
                "option_a": "1",
                "option_b": "2",
                "option_c": "3",
                "option_d": "4",
                "correct_options": ["B"],
                "response_to_user_option_a": "No",
                "response_to_user_option_b": "Yes",
                "response_to_user_option_c": "No",
                "response_to_user_option_d": "No",
                "quiz_take_away": "1+1=2",
            }
        ],
    )
    assert response.status_code == 400
    assert "Lesson 9999 not found" in response.json()["detail"]


def test_quiz_upload_accepts_existing_lesson(client, db_session):
    """Upload quiz questions with valid lesson_id succeeds."""
    _login(client, db_session)

    # Create lesson first
    create_resp = client.post(
        "/api/lessons",
        json={"topic": "math", "title": "Algebra"},
    )
    lesson_id = create_resp.json()["id"]

    response = client.post(
        "/api/quiz/questions",
        json=[
            {
                "topic_id": "math",
                "lesson_id": lesson_id,
                "lesson_filename": "test.md",
                "topic_name": "Math",
                "lesson_name": "Algebra",
                "quiz_type": "recall",
                "question": "What is 1+1?",
                "quiz_learnt": "Basic addition",
                "option_a": "1",
                "option_b": "2",
                "option_c": "3",
                "option_d": "4",
                "correct_options": ["B"],
                "response_to_user_option_a": "No",
                "response_to_user_option_b": "Yes",
                "response_to_user_option_c": "No",
                "response_to_user_option_d": "No",
                "quiz_take_away": "1+1=2",
            }
        ],
    )
    assert response.status_code == 200
    assert response.json()["inserted"] == 1
