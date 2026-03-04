"""User model for authentication and user management."""

from typing import Any, Dict

from sqlalchemy import Column, String, Integer

from ..database import Base


class Users(Base):
    """User model for authentication and user management."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"<User {self.id}>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary representation."""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
