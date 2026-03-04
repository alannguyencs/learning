"""Database configuration and session management for SQLAlchemy."""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

db_username = os.getenv("DB_USERNAME")
db_name = os.getenv("DB_NAME")
db_url = os.getenv("DB_URL")
db_password = os.getenv("DB_PASSWORD")

SQLALCHEMY_DB_URL = (
    f"postgresql://{db_username}:{db_password}@{db_url}:5432/{db_name}"
    if db_password
    else f"postgresql://{db_username}@{db_url}:5432/{db_name}"
)

engine = create_engine(
    SQLALCHEMY_DB_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Get a database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
