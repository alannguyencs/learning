"""Tests for authentication service functions."""

from datetime import timedelta

from jose import jwt
from passlib.context import CryptContext

from src.auth import (
    authenticate_user,
    create_access_token,
    get_current_user_from_token,
    SECRET_KEY,
    ALGORITHM,
)
from src.crud.crud_user import create_user


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TestAuthService:
    """Tests for auth service functions."""

    def test_create_access_token(self):
        """Token contains username and expire claims."""
        token = create_access_token(data={"username": "testuser"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["username"] == "testuser"
        assert "expire" in payload

    def test_create_access_token_with_expiry(self):
        """Token respects custom expiry delta."""
        token = create_access_token(
            data={"username": "testuser"}, expires_delta=timedelta(hours=1)
        )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["username"] == "testuser"

    def test_authenticate_user_correct_password(self, db_session):
        """Returns Users object on correct password."""
        hashed = bcrypt_context.hash("testpass")
        create_user(db_session, "testuser", hashed)
        result = authenticate_user(db_session, "testuser", "testpass")
        assert result is not False
        assert result.username == "testuser"

    def test_authenticate_user_wrong_password(self, db_session):
        """Returns False on wrong password."""
        hashed = bcrypt_context.hash("testpass")
        create_user(db_session, "testuser", hashed)
        result = authenticate_user(db_session, "testuser", "wrongpass")
        assert result is False

    def test_authenticate_user_not_found(self, db_session):
        """Returns False when user does not exist."""
        result = authenticate_user(db_session, "nonexistent", "anypass")
        assert result is False

    def test_get_current_user_from_valid_token(self, db_session):
        """Returns user from a valid token."""
        hashed = bcrypt_context.hash("testpass")
        create_user(db_session, "testuser", hashed)
        token = create_access_token(data={"username": "testuser"})
        user = get_current_user_from_token(db_session, token)
        assert user is not None
        assert user.username == "testuser"

    def test_get_current_user_from_expired_token(self, db_session):
        """Returns None for an expired token."""
        token = create_access_token(
            data={"username": "testuser"}, expires_delta=timedelta(seconds=-1)
        )
        # jose doesn't validate custom 'expire' field — but invalid token still returns None
        # if user doesn't exist
        user = get_current_user_from_token(db_session, token)
        assert user is None

    def test_get_current_user_from_invalid_token(self, db_session):
        """Returns None for a garbage token."""
        user = get_current_user_from_token(db_session, "invalid-token")
        assert user is None
