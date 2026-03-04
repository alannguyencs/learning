"""Tests for login API endpoints."""

from passlib.context import CryptContext

from src.crud.crud_user import create_user

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TestLoginEndpoints:
    """Tests for /api/login/ endpoints."""

    def test_login_success(self, client, db_session):
        """POST /api/login/ returns 200 and sets cookie on valid credentials."""
        hashed = bcrypt_context.hash("testpass")
        create_user(db_session, "testuser", hashed)

        response = client.post(
            "/api/login/", json={"username": "testuser", "password": "testpass"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["user"]["username"] == "testuser"
        assert "access_token" in response.cookies

    def test_login_wrong_credentials(self, client, db_session):
        """POST /api/login/ returns 401 on invalid credentials."""
        hashed = bcrypt_context.hash("testpass")
        create_user(db_session, "testuser", hashed)

        response = client.post(
            "/api/login/", json={"username": "testuser", "password": "wrongpass"}
        )
        assert response.status_code == 401
        assert response.json()["success"] is False

    def test_login_missing_fields(self, client):
        """POST /api/login/ returns 422 on missing fields."""
        response = client.post("/api/login/", json={"username": "testuser"})
        assert response.status_code == 422
