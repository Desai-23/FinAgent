# auth/jwt.py
# JWT token creation and verification

from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

# Secret key for signing tokens — in production this should be in .env
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "finagent-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def create_access_token(user_id: int, email: str) -> str:
    """Create a JWT token for a user that expires in 24 hours."""
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    """
    Verify a JWT token and return the payload if valid.
    Returns None if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        if user_id is None or email is None:
            return None
        return {"user_id": int(user_id), "email": email}
    except JWTError:
        return None





