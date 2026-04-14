# api/auth_routes.py
# Authentication endpoints: register, login, profile

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth.models import get_db
from auth.schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from auth.service import get_user_by_email, create_user, authenticate_user
from auth.jwt import create_access_token
from auth.dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
def register(request: UserRegister, db: Session = Depends(get_db)):
    """
    Create a new user account.
    Returns a JWT token immediately so user is logged in after registering.
    """
    # Check if email already exists
    existing = get_user_by_email(db, request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    # Validate password length
    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters.",
        )

    # Create the user
    user = create_user(db, request.email, request.password, request.full_name)

    # Return JWT token + user info
    token = create_access_token(user.id, user.email)
    return TokenResponse(
        access_token=token,
        user=UserResponse.from_orm(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(request: UserLogin, db: Session = Depends(get_db)):
    """
    Log in with email and password.
    Returns a JWT token valid for 24 hours.
    """
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    token = create_access_token(user.id, user.email)
    return TokenResponse(
        access_token=token,
        user=UserResponse.from_orm(user),
    )


@router.get("/me", response_model=UserResponse)
def get_profile(current_user=Depends(get_current_user)):
    """
    Get the current logged-in user's profile.
    Requires a valid JWT token in the Authorization header.
    """
    return current_user

