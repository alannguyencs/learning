"""Tests for auth-related API endpoints (/api/me, logout)."""

from passlib.context import CryptContext

from src.crud.crud_user import create_user

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TestAuthEndpoints:
    """Tests for /api/me and logout endpoints."""

    def test_me_authenticated(self, client, db_session):
        """GET /api/me with valid cookie returns authenticated: true."""
        hashed = bcrypt_context.hash("testpass")
        create_user(db_session, "testuser", hashed)

        # Login first to get cookie
        client.post("/api/login/", json={"username": "testuser", "password": "testpass"})

        response = client.get("/api/me")
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert data["user"]["username"] == "testuser"

    def test_me_unauthenticated(self, client):
        """GET /api/me without cookie returns authenticated: false."""
        response = client.get("/api/me")
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert data["user"] is None

    def test_logout(self, client, db_session):
        """POST /api/login/logout deletes cookie."""
        hashed = bcrypt_context.hash("testpass")
        create_user(db_session, "testuser", hashed)

        # Login first
        client.post("/api/login/", json={"username": "testuser", "password": "testpass"})

        # Logout
        response = client.post("/api/login/logout")
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Verify no longer authenticated
        response = client.get("/api/me")
        assert response.json()["authenticated"] is False
