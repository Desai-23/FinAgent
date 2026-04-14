# auth/service.py
# Business logic for register, login, get user
# Uses bcrypt directly (bypasses passlib compatibility issue with bcrypt 5.x)

import bcrypt
import hashlib
from sqlalchemy.orm import Session
from auth.models import User
from typing import Optional


def _prepare_password(password: str) -> bytes:
    """
    SHA256-hash the password first, then encode to bytes.
    This bypasses bcrypt's 72-byte limit safely.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("utf-8")


def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt."""
    prepared = _prepare_password(password)
    hashed = bcrypt.hashpw(prepared, bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Check if a plain password matches the hashed version."""
    prepared = _prepare_password(plain)
    return bcrypt.checkpw(prepared, hashed.encode("utf-8"))


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Find a user by their email address."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Find a user by their ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, password: str, full_name: str = None) -> User:
    """Create a new user with a hashed password."""
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user








def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Verify email and password.
    Returns the User object if valid, None if invalid.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user




