"""Authentication and user schemas."""

from pydantic import BaseModel


class Token(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    """Schema for login request."""

    username: str
    password: str


class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)."""

    id: int
    username: str

    class Config:
        """Pydantic configuration for ORM mode compatibility."""

        from_attributes = True
