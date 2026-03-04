"""QuizLog model — per quiz served to a user."""

from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index, JSON

from ..database import Base


class QuizLog(Base):
    """Track quiz attempts per user."""

    __tablename__ = "quiz_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey("users.username"), nullable=False)
    quiz_question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    topic_id = Column(String, nullable=False)
    lesson_id = Column(Integer, nullable=False)
    quiz_type = Column(String, nullable=False)
    user_answer = Column(JSON, nullable=True)
    assessment_result = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_ql_user_topic", "username", "topic_id"),
        Index("idx_ql_user_lesson", "username", "lesson_id"),
        Index("idx_ql_user_created", "username", "created_at"),
    )
