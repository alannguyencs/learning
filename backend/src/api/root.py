"""Root API endpoints including current user verification."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from src.auth import authenticate_user_from_request
from src.database import get_db

router = APIRouter()


@router.get("/me")
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get current authenticated user from session cookie."""
    user = authenticate_user_from_request(request, db)

    if not user:
        return {"authenticated": False, "user": None}

    return {
        "authenticated": True,
        "user": {"id": user.id, "username": user.username},
    }
