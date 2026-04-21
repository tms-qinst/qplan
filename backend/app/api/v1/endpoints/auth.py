"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import verify_token, get_current_user
from app.models.user import User
from app.schemas.schemas import TokenResponse, UserResponse, UserCreate

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """Register a new application user after Supabase Auth signup."""
    existing = db.query(User).filter(User.auth_user_id == user_data.auth_user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already registered")

    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        auth_user_id=user_data.auth_user_id,
        full_name=user_data.full_name,
        email=user_data.email,
        role_id=user_data.role_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user info."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    full_name: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user profile."""
    if full_name:
        current_user.full_name = full_name
    db.commit()
    db.refresh(current_user)
    return current_user