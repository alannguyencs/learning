"""API routes for user login with cookie-based sessions."""

import logging

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.auth import authenticate_user, create_access_token
from src.database import get_db
from src.schemas import LoginRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/login", tags=["login"])


@router.post("/")
async def process_login(login_data: LoginRequest, db: Session = Depends(get_db)) -> JSONResponse:
    """Handle POST request for user login."""
    user = authenticate_user(db, login_data.username, login_data.password)

    if not user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"success": False, "message": "Invalid username or password"},
        )

    access_token = create_access_token(data={"username": login_data.username})

    response = JSONResponse(
        content={
            "success": True,
            "message": "Login successful",
            "user": {"id": user.id, "username": user.username},
        }
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=7776000,
        path="/",
    )

    return response


@router.post("/logout")
async def logout() -> JSONResponse:
    """Handle user logout."""
    response = JSONResponse(content={"success": True, "message": "Logout successful"})
    response.delete_cookie(key="access_token")
    return response
