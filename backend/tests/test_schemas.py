"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from src.schemas import Token, LoginRequest, UserResponse


def test_login_request_valid():
    """Accepts valid username + password."""
    req = LoginRequest(username="testuser", password="testpass")
    assert req.username == "testuser"
    assert req.password == "testpass"


def test_login_request_missing_field():
    """Raises validation error on missing field."""
    with pytest.raises(ValidationError):
        LoginRequest(username="testuser")


def test_token_schema():
    """Token schema with access_token + token_type."""
    token = Token(access_token="abc123", token_type="bearer")
    assert token.access_token == "abc123"
    assert token.token_type == "bearer"


def test_user_response_from_orm():
    """UserResponse works with from_attributes = True."""
    user = UserResponse(id=1, username="testuser", role="admin")
    assert user.id == 1
    assert user.username == "testuser"
    assert user.role == "admin"


def test_user_response_optional_role():
    """UserResponse role defaults to None."""
    user = UserResponse(id=1, username="testuser")
    assert user.role is None
