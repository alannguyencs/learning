"""Recall dashboard service — computes recall map and topic matrix."""

import logging
from collections import defaultdict
from typing import Dict, List

from sqlalchemy.orm import Session

from src.crud.crud_lesson_memory import get_all_lesson_memories
from src.crud.crud_quiz_log import get_all_quiz_logs, get_user_total_quiz_count
from src.crud.crud_topic_memory import get_all_memory_states
from src.models.user_lesson_memory import UserLessonMemory
from src.schemas.recall_dashboard import (
    LessonRecallItem,
    RecallMapResponse,
    TopicMatrixResponse,
    TopicMatrixRow,
    TopicQuizAttempt,
    TopicRecallItem,
)
from src.service.topic_lookup import (
    get_all_topic_ids,
    get_lesson_count,
    get_lesson_name,
    get_lessons_for_topic,
    get_topic_name,
)

logger = logging.getLogger(__name__)

AT_RISK_THRESHOLD = 0.5


class RecallService:
    """Compute two-level recall map and topic quiz matrix."""

    @staticmethod
    def get_recall_map(db: Session, username: str) -> RecallMapResponse:
        """Compute two-level recall map.

        1. Load all UserTopicMemory, UserLessonMemory, quiz count
        2. For each topic: compute topic m(t), then for each lesson compute lesson m(t)
        3. Never-reviewed: m(t) = 1.0 (neutral, not alarming)
        4. Compute global_recall = mean of topic m(t)s
        5. Count topics_at_risk (m(t) < 0.5), lessons_at_risk (m(t) < 0.5)
        """
        current_quiz_count = get_user_total_quiz_count(db, username)
        topic_memories = get_all_memory_states(db, username)
        lesson_memories = get_all_lesson_memories(db, username)

        # Index topic memories by topic_id
        topic_mem_map = {tm.topic_id: tm for tm in topic_memories}

        # Index lesson memories by topic_id
        lesson_mem_by_topic: Dict[str, List[UserLessonMemory]] = defaultdict(list)
        for lm in lesson_memories:
            lesson_mem_by_topic[lm.topic_id].append(lm)

        all_topic_ids = get_all_topic_ids()
        topics: List[TopicRecallItem] = []
        topics_at_risk = 0
        lessons_at_risk = 0

        for tid in all_topic_ids:
            tm = topic_mem_map.get(tid)
            if tm:
                topic_recall = tm.recall_probability(current_quiz_count)
                topic_forgetting = tm.forgetting_rate
                topic_last_review = tm.last_review_at
                topic_review_count = tm.review_count
                topic_correct_count = tm.correct_count
            else:
                topic_recall = 1.0
                topic_forgetting = 0.3
                topic_last_review = None
                topic_review_count = 0
                topic_correct_count = 0

            if topic_recall < AT_RISK_THRESHOLD:
                topics_at_risk += 1

            # Build lesson list
            lesson_mems = {lm.lesson_id: lm for lm in lesson_mem_by_topic.get(tid, [])}
            lesson_ids = get_lessons_for_topic(tid)
            lesson_items: List[LessonRecallItem] = []

            for lid in lesson_ids:
                lm = lesson_mems.get(lid)
                if lm:
                    lesson_recall = lm.recall_probability(current_quiz_count)
                    lesson_item = LessonRecallItem(
                        lesson_id=lid,
                        lesson_name=get_lesson_name(lid),
                        recall_probability=lesson_recall,
                        forgetting_rate=lm.forgetting_rate,
                        last_review_at=lm.last_review_at,
                        review_count=lm.review_count,
                        correct_count=lm.correct_count,
                    )
                else:
                    lesson_recall = 1.0
                    lesson_item = LessonRecallItem(
                        lesson_id=lid,
                        lesson_name=get_lesson_name(lid),
                        recall_probability=1.0,
                        forgetting_rate=0.3,
                        last_review_at=None,
                        review_count=0,
                        correct_count=0,
                    )

                if lesson_recall < AT_RISK_THRESHOLD:
                    lessons_at_risk += 1

                lesson_items.append(lesson_item)

            topics.append(
                TopicRecallItem(
                    topic_id=tid,
                    topic_name=get_topic_name(tid),
                    lesson_count=get_lesson_count(tid),
                    recall_probability=topic_recall,
                    forgetting_rate=topic_forgetting,
                    last_review_at=topic_last_review,
                    review_count=topic_review_count,
                    correct_count=topic_correct_count,
                    lessons=lesson_items,
                )
            )

        global_recall = (
            sum(t.recall_probability for t in topics) / len(topics) if topics else 1.0
        )

        return RecallMapResponse(
            topics=topics,
            global_recall=round(global_recall, 4),
            topics_at_risk=topics_at_risk,
            lessons_at_risk=lessons_at_risk,
        )

    @staticmethod
    def get_topic_matrix(db: Session, username: str) -> TopicMatrixResponse:
        """Build quiz history grid.

        1. Load all QuizLog ordered by created_at
        2. Assign global column_index (1-based, chronological)
        3. Group by topic_id into rows
        4. Each cell: quiz_id, result, asked_at, column_index, lesson_name
        """
        logs = get_all_quiz_logs(db, username)

        # Group by topic_id, preserving chronological column_index
        topic_quizzes: Dict[str, List[TopicQuizAttempt]] = defaultdict(list)
        topic_last_quiz: Dict[str, object] = {}

        for idx, log in enumerate(logs, start=1):
            attempt = TopicQuizAttempt(
                quiz_id=log.id,
                result=log.assessment_result,
                asked_at=log.created_at,
                column_index=idx,
                lesson_name=get_lesson_name(log.lesson_id),
            )
            topic_quizzes[log.topic_id].append(attempt)
            topic_last_quiz[log.topic_id] = log.created_at

        # Build rows for all topics (include topics with no quizzes)
        all_topic_ids = get_all_topic_ids()
        rows: List[TopicMatrixRow] = []

        for tid in all_topic_ids:
            quizzes = topic_quizzes.get(tid, [])
            rows.append(
                TopicMatrixRow(
                    topic_id=tid,
                    topic_name=get_topic_name(tid),
                    lesson_count=get_lesson_count(tid),
                    last_quiz_at=topic_last_quiz.get(tid),
                    quizzes=quizzes,
                )
            )

        max_quiz_count = len(logs)

        return TopicMatrixResponse(topics=rows, max_quiz_count=max_quiz_count)
