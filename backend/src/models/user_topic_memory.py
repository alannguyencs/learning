"""User topic memory model for MEMORIZE-based quiz scheduling.

Reference: Tabibian et al., "Enhancing Human Learning via Spaced Repetition Optimization"
           (PNAS 2019)
"""

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

QUIZ_DECAY_SCALE = 10
N_MAX = 1.5


class UserTopicMemory(Base):
    """Track per-topic memory state for MEMORIZE scheduling.

    m(t) = exp(-n * quizzes_elapsed / QUIZ_DECAY_SCALE)
    """

    __tablename__ = "user_topic_memory"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey("users.username"), nullable=False)
    topic_id = Column(String, nullable=False)
    forgetting_rate = Column(Float, nullable=False, default=0.3)
    last_review_at = Column(DateTime, nullable=True)
    last_review_quiz_count = Column(Integer, nullable=False, default=0)
    review_count = Column(Integer, nullable=False, default=0)
    correct_count = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        CheckConstraint("forgetting_rate > 0", name="ck_topic_forgetting_rate_positive"),
        UniqueConstraint("username", "topic_id", name="uq_user_topic_memory"),
        Index("idx_topic_memory_user_topic", "username", "topic_id"),
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
