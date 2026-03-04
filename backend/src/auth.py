"""Authentication utilities for JWT token generation and user verification."""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.crud.crud_user import get_user_by_username
from src.models import Users

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 7_776_000  # 90 days

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def authenticate_user(db: Session, username: str, password: str) -> Union[Users, bool]:
    """Authenticate user with provided username and password."""
    user = get_user_by_username(db, username)

    if not user:
        return False

    if not bcrypt_context.verify(password, user.hashed_password):
        return False

    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)

    to_encode.update({"expire": expire.isoformat()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_current_user_from_token(db: Session, token: str) -> Optional[Users]:
    """Validate JWT token and return the corresponding user."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")

        if username is None:
            return None

        user = get_user_by_username(db, username)
        return user

    except JWTError:
        return None


def authenticate_user_from_request(request: Request, db: Session) -> Union[Users, bool]:
    """Authenticate user from HTTP request using session cookie."""
    token = request.cookies.get("access_token")
    if not token:
        return False

    user = get_current_user_from_token(db, token)
    if not user:
        return False

    return user
