"""Tests for ORM models."""

from src.models import Users
from src.crud.crud_user import create_user


def test_users_table_name():
    """Users model has correct table name."""
    assert Users.__tablename__ == "users"


def test_users_to_dict(db_session):
    """to_dict() serialization includes id, username."""
    user = create_user(db_session, "testuser", "hashedpass")
    user_dict = user.to_dict()
    assert user_dict["username"] == "testuser"
    assert "id" in user_dict
    assert "hashed_password" in user_dict
