import datetime
from typing import Any

import jwt

from helix_platform.config import get_settings

settings = get_settings()

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(
    user_id: str, email: str, expires_delta: datetime.timedelta | None = None
) -> str:
    """Generates a secure access JWT."""
    if expires_delta:
        expire = datetime.datetime.now(datetime.UTC) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"sub": user_id, "email": email, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(
    user_id: str, expires_delta: datetime.timedelta | None = None
) -> str:
    """Generates a secure refresh JWT."""
    if expires_delta:
        expire = datetime.datetime.now(datetime.UTC) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode = {"sub": user_id, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decodes a JWT and validates its expiration and structure.

    Raises:
        jwt.ExpiredSignatureError: if token is expired.
        jwt.InvalidTokenError: if token is otherwise invalid.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
