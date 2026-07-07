from typing import Any

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from helix_platform.persistence import get_db
from services.identity.jwt import decode_token
from services.identity.models import UserDB


async def get_current_user_optional(
    request: Request, db: Session = Depends(get_db)
) -> UserDB | None:
    """Attempts to extract and authenticate user from Bearer token or HTTP cookies."""
    # 1. Try to extract token from Authorization header
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    # 2. Try to extract from cookie if not found in header
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        return None

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

    return db.query(UserDB).filter(UserDB.id == user_id).first()


async def get_current_user(
    user: UserDB | None = Depends(get_current_user_optional),
) -> UserDB:
    """Ensures a valid authenticated user session is active, raising HTTP 401 if not."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


class JWTRouteProtectionMiddleware(BaseHTTPMiddleware):
    """Base HTTP middleware class providing automated JWT protection on specific path prefixes."""  # noqa: E501

    def __init__(self, app: Any, protected_prefixes: list[str] | None = None) -> None:
        super().__init__(app)
        self.protected_prefixes = protected_prefixes or []

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        path = request.url.path
        is_protected = any(
            path.startswith(prefix) for prefix in self.protected_prefixes
        )

        if is_protected:
            token = None
            auth_header = request.headers.get("Authorization")
            if auth_header:
                parts = auth_header.split()
                if len(parts) == 2 and parts[0].lower() == "bearer":
                    token = parts[1]
            if not token:
                token = request.cookies.get("access_token")

            if not token:
                return JSONResponse(
                    status_code=401, content={"detail": "Authentication token missing"}
                )

            try:
                payload = decode_token(token)
                if payload.get("type") != "access":
                    return JSONResponse(
                        status_code=401, content={"detail": "Invalid token type"}
                    )
                # Attach token metadata on request state
                request.state.user_id = payload.get("sub")
                request.state.user_email = payload.get("email")
            except jwt.ExpiredSignatureError:
                return JSONResponse(
                    status_code=401, content={"detail": "Token expired"}
                )
            except jwt.InvalidTokenError:
                return JSONResponse(
                    status_code=401, content={"detail": "Invalid authentication token"}
                )

        return await call_next(request)
