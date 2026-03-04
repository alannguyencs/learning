"""QuizQuestion model — pre-generated question bank with flat columns."""

from datetime import datetime

from sqlalchemy import Column, String, Integer, Text, DateTime, Index, JSON

from ..database import Base


class QuizQuestion(Base):
    """Pre-generated quiz question with flat columns (no JSON blob)."""

    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(String, nullable=False)
    lesson_id = Column(Integer, nullable=False)
    lesson_filename = Column(String, nullable=False)
    quiz_type = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    quiz_learnt = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_options = Column(JSON, nullable=False)
    response_to_user_option_a = Column(Text, nullable=False)
    response_to_user_option_b = Column(Text, nullable=False)
    response_to_user_option_c = Column(Text, nullable=False)
    response_to_user_option_d = Column(Text, nullable=False)
    quiz_take_away = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_qq_topic_lesson_type", "topic_id", "lesson_id", "quiz_type"),
        Index("idx_qq_lesson_type", "lesson_id", "quiz_type"),
    )

    def get_options(self) -> dict:
        """Return options as {A: ..., B: ..., C: ..., D: ...}."""
        return {
            "A": self.option_a,
            "B": self.option_b,
            "C": self.option_c,
            "D": self.option_d,
        }

    def get_explanations(self) -> dict:
        """Return all 4 explanations as {A: ..., B: ..., C: ..., D: ...}."""
        return {
            "A": self.response_to_user_option_a,
            "B": self.response_to_user_option_b,
            "C": self.response_to_user_option_c,
            "D": self.response_to_user_option_d,
        }
