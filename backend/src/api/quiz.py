"""API routes for quiz system."""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.auth import authenticate_user_from_request
from src.crud.crud_quiz_log import (
    create_quiz_log,
    get_quiz_history,
    get_quiz_log_by_id,
    get_quiz_stats,
)
from src.crud.crud_lesson import get_lesson_by_id
from src.crud.crud_quiz_question import (
    create_quiz_questions,
    get_question_by_id,
    get_question_count,
    get_question_count_for_topic,
    get_total_question_count,
)
from src.database import get_db
from src.schemas.quiz import (
    LessonItem,
    QuizAnswerRequest,
    QuizAnswerResponse,
    QuizBulkCreateResponse,
    QuizEligibilityResponse,
    QuizHistoryItem,
    QuizNextResponse,
    QuizQuestionCreate,
    QuizStatsResponse,
    TopicWithLessons,
)
from src.service.answer_service import grade_and_update
from src.service.quiz_selector import LOOP_SIZE_CAP, select_quiz
from src.service.topic_lookup import (
    get_all_topic_ids,
    get_lesson_name,
    get_lessons_for_topic,
    get_topic_name,
    register_topic,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


def _get_user_or_401(request: Request, db: Session):
    """Authenticate user or raise 401."""
    user = authenticate_user_from_request(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


@router.get("/next", response_model=QuizNextResponse)
async def get_next_quiz(
    request: Request,
    db: Session = Depends(get_db),
    topic_id: Optional[str] = None,
    lesson_id: Optional[int] = None,
):
    """Get the next quiz question based on MEMORIZE algorithm."""
    user = _get_user_or_401(request, db)

    question = select_quiz(db, user.username, topic_id=topic_id, lesson_id=lesson_id)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No quiz questions available for the selected scope",
        )

    quiz_log = create_quiz_log(
        db,
        username=user.username,
        quiz_question_id=question.id,
        topic_id=question.topic_id,
        lesson_id=question.lesson_id,
        quiz_type=question.quiz_type,
    )

    lesson_q_count = get_question_count(db, question.lesson_id)
    if lesson_id is not None:
        loop_count = lesson_q_count
    elif topic_id is not None:
        loop_count = min(LOOP_SIZE_CAP, get_question_count_for_topic(db, topic_id))
    else:
        loop_count = min(LOOP_SIZE_CAP, get_total_question_count(db))

    return QuizNextResponse(
        quiz_id=quiz_log.id,
        question=question.question,
        options=question.get_options(),
        quiz_type=question.quiz_type,
        topic_id=question.topic_id,
        lesson_id=question.lesson_id,
        lesson_title=get_lesson_name(question.lesson_id),
        correct_option_count=len(question.correct_options),
        lesson_question_count=lesson_q_count,
        loop_question_count=loop_count,
    )


@router.post("/{quiz_id}/answer", response_model=QuizAnswerResponse)
async def answer_quiz(
    request: Request,
    quiz_id: int,
    body: QuizAnswerRequest,
    db: Session = Depends(get_db),
):
    """Submit an answer to a quiz."""
    user = _get_user_or_401(request, db)

    quiz_log = get_quiz_log_by_id(db, quiz_id)
    if not quiz_log or quiz_log.username != user.username:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    if quiz_log.assessment_result is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz already answered"
        )

    result = grade_and_update(db, quiz_id, body.answer)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to grade answer",
        )

    return QuizAnswerResponse(**result)


@router.get("/history")
async def quiz_history(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
):
    """Get paginated quiz history."""
    user = _get_user_or_401(request, db)

    logs = get_quiz_history(db, user.username, limit=limit, offset=offset)
    items = []
    for log in logs:
        question = get_question_by_id(db, log.quiz_question_id)
        items.append(
            QuizHistoryItem(
                quiz_id=log.id,
                topic_id=log.topic_id,
                lesson_id=log.lesson_id,
                quiz_type=log.quiz_type,
                question=question.question if question else "",
                user_answer=log.user_answer,
                assessment_result=log.assessment_result,
                created_at=log.created_at,
            )
        )

    return {"quizzes": items}


@router.get("/stats", response_model=QuizStatsResponse)
async def quiz_stats(request: Request, db: Session = Depends(get_db)):
    """Get quiz statistics."""
    user = _get_user_or_401(request, db)
    stats = get_quiz_stats(db, user.username)
    return QuizStatsResponse(**stats)


@router.get("/eligibility", response_model=QuizEligibilityResponse)
async def quiz_eligibility(request: Request, db: Session = Depends(get_db)):
    """Check if user has quiz questions available."""
    user = _get_user_or_401(request, db)

    total = get_total_question_count(db)
    if total == 0:
        return QuizEligibilityResponse(eligible=False, reason="No quiz questions in the bank")

    return QuizEligibilityResponse(eligible=True, reason="Quiz questions available")


@router.get("/topics")
async def get_topics(request: Request, db: Session = Depends(get_db)):
    """Get all topics with nested lessons for scope filter."""
    _get_user_or_401(request, db)

    topics = []
    for tid in get_all_topic_ids():
        lessons = [
            LessonItem(lesson_id=lid, lesson_name=get_lesson_name(lid))
            for lid in get_lessons_for_topic(tid)
        ]
        topics.append(
            TopicWithLessons(
                topic_id=tid,
                topic_name=get_topic_name(tid),
                lessons=lessons,
            )
        )

    return {"topics": topics}


@router.post("/questions", response_model=QuizBulkCreateResponse)
async def create_questions(
    request: Request,
    questions: List[QuizQuestionCreate],
    db: Session = Depends(get_db),
):
    """Bulk-create quiz questions."""
    _get_user_or_401(request, db)

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No questions provided"
        )

    # Validate that all referenced lesson_ids exist in lessons table
    lesson_ids = {q.lesson_id for q in questions}
    for lid in lesson_ids:
        if not get_lesson_by_id(db, lid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Lesson {lid} not found. Create it first via POST /api/lessons.",
            )

    dicts = [q.model_dump() for q in questions]
    count = create_quiz_questions(db, dicts)

    # Auto-register topics/lessons in memory cache
    seen = set()
    for q in questions:
        key = (q.topic_id, q.lesson_id)
        if key not in seen:
            seen.add(key)
            register_topic(
                topic_id=q.topic_id,
                topic_name=q.topic_name,
                lesson_id=q.lesson_id,
                lesson_name=q.lesson_name,
                lesson_filename=q.lesson_filename,
            )

    return QuizBulkCreateResponse(
        inserted=count,
        lesson_id=questions[0].lesson_id,
        topic_id=questions[0].topic_id,
    )
