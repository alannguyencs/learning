"""Tests for quiz Pydantic schemas."""

import pytest
from pydantic import ValidationError

from src.schemas.quiz import (
    QuizAnswerRequest,
    QuizNextResponse,
    QuizAnswerResponse,
    QuizStatsResponse,
)


def test_quiz_answer_request_valid_single():
    """Accepts ["B"]."""
    req = QuizAnswerRequest(answer=["B"])
    assert req.answer == ["B"]


def test_quiz_answer_request_valid_multi():
    """Accepts ["A", "C"]."""
    req = QuizAnswerRequest(answer=["A", "C"])
    assert req.answer == ["A", "C"]


def test_quiz_answer_request_empty():
    """Rejects empty list."""
    with pytest.raises(ValidationError):
        QuizAnswerRequest(answer=[])


def test_quiz_next_response():
    """All fields present."""
    resp = QuizNextResponse(
        quiz_id=1,
        question="What?",
        options={"A": "a", "B": "b", "C": "c", "D": "d"},
        quiz_type="recall",
        topic_id="t1",
        lesson_id=1,
        lesson_title="Test Lesson",
        correct_option_count=1,
        lesson_question_count=10,
        loop_question_count=10,
    )
    assert resp.quiz_id == 1
    assert resp.quiz_type == "recall"
    assert resp.correct_option_count == 1
    assert resp.lesson_question_count == 10


def test_quiz_answer_response():
    """Includes quiz_learnt, explanations, quiz_take_away."""
    resp = QuizAnswerResponse(
        is_correct=True,
        correct_options=["B"],
        quiz_learnt="Learning about X",
        explanations={"A": "eA", "B": "eB", "C": "eC", "D": "eD"},
        quiz_take_away="Key takeaway",
    )
    assert resp.quiz_learnt == "Learning about X"
    assert len(resp.explanations) == 4


def test_quiz_stats_response():
    """Stats schema."""
    resp = QuizStatsResponse(total=10, correct=7, accuracy=0.7)
    assert resp.accuracy == 0.7
