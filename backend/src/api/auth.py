"""API endpoint for user authentication via JWT tokens (OAuth2 flow)."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.auth import authenticate_user, create_access_token
from src.database import get_db
from src.schemas import Token

router = APIRouter()

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    """Generate JWT access token for authenticated users."""
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"username": form_data.username})

    return Token(access_token=access_token, token_type="bearer")
