"""CRUD operations for User model."""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from src.models import Users

logger = logging.getLogger(__name__)


def get_user_by_username(db: Session, username: str) -> Optional[Users]:
    """Get a user by username."""
    return db.query(Users).filter(Users.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[Users]:
    """Get a user by ID."""
    return db.query(Users).filter(Users.id == user_id).first()


def create_user(db: Session, username: str, hashed_password: str) -> Users:
    """Create a new user."""
    db_user = Users(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_password(db: Session, user_id: int, new_hashed_password: str) -> Optional[Users]:
    """Update user password."""
    user = db.query(Users).filter(Users.id == user_id).first()
    if user:
        user.hashed_password = new_hashed_password
        db.commit()
        db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user."""
    user = db.query(Users).filter(Users.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False
