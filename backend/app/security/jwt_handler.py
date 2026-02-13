import jwt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.config import settings
from app.security.hsm_client import keys


def create_jwt_token(user_id: str, username: str) -> str:
    """Create a short-lived JWT token."""
    payload = {
        "sub": user_id,
        "username": username,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRY_MINUTES),
        "jti": secrets.token_hex(16),
    }
    return jwt.encode(payload, keys.get_jwt_secret(), algorithm=settings.JWT_ALGORITHM)


def verify_jwt_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    try:
        return jwt.decode(token, keys.get_jwt_secret(), algorithms=[settings.JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
