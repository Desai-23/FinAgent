# auth/schemas.py
# Pydantic schemas — defines the shape of request and response data

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserRegister(BaseModel):
    """Request body for POST /auth/register"""
    email: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """Request body for POST /auth/login"""
    email: str
    password: str


class UserResponse(BaseModel):
    """What we send back about a user — never includes password"""
    id: int
    email: str
    full_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Response after successful login"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
