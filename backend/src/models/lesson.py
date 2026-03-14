"""Lesson model — normalized lesson records."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Date, Index, Integer, String, Text

from ..database import Base


class Lesson(Base):
    """A lesson record with topic, title, published date, and content."""

    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    topic_name = Column(String, nullable=True)
    title = Column(String, nullable=False)
    published_date = Column(Date, nullable=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (Index("idx_lessons_topic", "topic"),)
