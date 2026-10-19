from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
import jwt
from src.config import settings


def generate_password_hash(password: str) -> str:
    """Generate bcrypt password hash."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(user_data: dict, expiry: Optional[timedelta] = None) -> str:
    """Create JWT access token with expiration."""
    payload = user_data.copy()
    expire_time = datetime.now(timezone.utc) + (
        expiry if expiry else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expire_time})

    token = jwt.encode(
        payload,
        key=settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        token_data = jwt.decode(
            token,
            key=settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return token_data
    except jwt.PyJWTError:
        return None
