"""User lesson memory model — lesson-level MEMORIZE tracking."""

import math

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint,
    UniqueConstraint,
)

from ..database import Base
from .user_topic_memory import QUIZ_DECAY_SCALE, N_MAX


class UserLessonMemory(Base):
    """Track per-lesson memory state for MEMORIZE scheduling.

    Same formula as UserTopicMemory but at lesson granularity.
    Includes topic_id for grouping.
    """

    __tablename__ = "user_lesson_memory"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey("users.username"), nullable=False)
    topic_id = Column(String, nullable=False)
    lesson_id = Column(Integer, nullable=False)
    forgetting_rate = Column(Float, nullable=False, default=0.3)
    last_review_at = Column(DateTime, nullable=True)
    last_review_quiz_count = Column(Integer, nullable=False, default=0)
    review_count = Column(Integer, nullable=False, default=0)
    correct_count = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        CheckConstraint("forgetting_rate > 0", name="ck_lesson_forgetting_rate_positive"),
        UniqueConstraint("username", "lesson_id", name="uq_user_lesson_memory"),
        Index("idx_lesson_memory_user_topic", "username", "topic_id"),
    )

    def recall_probability(self, current_quiz_count: int) -> float:
        """Compute m(t) = exp(-n * quizzes_elapsed / QUIZ_DECAY_SCALE).

        Returns 1.0 if never reviewed (record exists but no actual reviews).
        """
        if self.review_count == 0 or self.last_review_quiz_count is None:
            return 1.0
        quizzes_elapsed = max(0, current_quiz_count - self.last_review_quiz_count)
        return math.exp(-self.forgetting_rate * quizzes_elapsed / QUIZ_DECAY_SCALE)

    def update_on_correct(self, alpha: float = 0.3) -> None:
        """Memory strengthens: n *= (1 - alpha)."""
        self.forgetting_rate = max(0.01, self.forgetting_rate * (1.0 - alpha))

    def update_on_incorrect(self, beta: float = 0.2) -> None:
        """Memory weakens: n *= (1 + beta), capped at N_MAX."""
        self.forgetting_rate = min(N_MAX, self.forgetting_rate * (1.0 + beta))
