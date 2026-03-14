"""API routes for recall dashboard — recall map and topic matrix."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.auth import authenticate_user_from_request
from src.database import get_db
from src.schemas.recall_dashboard import RecallMapResponse, TopicMatrixResponse
from src.service.recall_service import RecallService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quiz", tags=["dashboard"])


def _get_user_or_401(request: Request, db: Session):
    """Authenticate user or raise 401."""
    user = authenticate_user_from_request(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


@router.get("/recall-map", response_model=RecallMapResponse)
async def get_recall_map(request: Request, db: Session = Depends(get_db)):
    """Get two-level recall map with topic and lesson recall probabilities."""
    user = _get_user_or_401(request, db)
    return RecallService.get_recall_map(db, user.username)


@router.get("/topic-matrix", response_model=TopicMatrixResponse)
async def get_topic_matrix(request: Request, db: Session = Depends(get_db)):
    """Get quiz history matrix grouped by topic."""
    user = _get_user_or_401(request, db)
    return RecallService.get_topic_matrix(db, user.username)
