"""Tests for user CRUD operations."""

import pytest
from sqlalchemy.exc import IntegrityError

from src.crud.crud_user import (
    get_user_by_username,
    get_user_by_id,
    create_user,
    update_user_password,
    delete_user,
)


class TestUserCRUD:
    """Tests for user CRUD functions."""

    def test_create_user(self, db_session):
        """Inserts and returns user."""
        user = create_user(db_session, "testuser", "hashedpass")
        assert user.username == "testuser"
        assert user.hashed_password == "hashedpass"
        assert user.id is not None

    def test_get_user_by_username(self, db_session):
        """Returns user when found."""
        create_user(db_session, "testuser", "hashedpass")
        user = get_user_by_username(db_session, "testuser")
        assert user is not None
        assert user.username == "testuser"

    def test_get_user_by_username_not_found(self, db_session):
        """Returns None when user not found."""
        user = get_user_by_username(db_session, "nonexistent")
        assert user is None

    def test_get_user_by_id(self, db_session):
        """Returns user when found by ID."""
        created = create_user(db_session, "testuser", "hashedpass")
        user = get_user_by_id(db_session, created.id)
        assert user is not None
        assert user.username == "testuser"

    def test_create_duplicate_username(self, db_session):
        """Raises IntegrityError on duplicate username."""
        create_user(db_session, "testuser", "hashedpass")
        with pytest.raises(IntegrityError):
            create_user(db_session, "testuser", "hashedpass2")

    def test_update_user_password(self, db_session):
        """Updates password successfully."""
        user = create_user(db_session, "testuser", "oldpass")
        updated = update_user_password(db_session, user.id, "newpass")
        assert updated.hashed_password == "newpass"

    def test_delete_user(self, db_session):
        """Deletes user and returns True."""
        user = create_user(db_session, "testuser", "hashedpass")
        result = delete_user(db_session, user.id)
        assert result is True
        assert get_user_by_id(db_session, user.id) is None

    def test_delete_user_not_found(self, db_session):
        """Returns False when user not found."""
        result = delete_user(db_session, 999)
        assert result is False
