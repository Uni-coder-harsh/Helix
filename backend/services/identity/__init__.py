import uuid
from typing import Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from helix_platform.config import get_settings
from helix_platform.persistence import get_db

from .crypto import hash_password, verify_password
from .jwt import create_access_token, create_refresh_token, decode_token
from .middleware import get_current_user
from .models import UserDB
from .schemas import (
    ForgotPasswordRequest,
    RefreshRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    VerifyEmailRequest,
)

settings = get_settings()

router = APIRouter(prefix="/identity", tags=["Identity"])

# Import UserDB to register model metadata for migrations/startup tables
__all__ = ["UserDB", "router"]


@router.get("")
@router.get("/")
def get_root() -> dict[str, str]:
    """Identity Service status endpoint."""
    return {"service": "Identity Service", "status": "active"}


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    payload: UserRegisterRequest, db: Session = Depends(get_db)
) -> UserResponse:
    # Check if user already exists
    existing_user = db.query(UserDB).filter(UserDB.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    hashed = hash_password(payload.password)
    verification_token = str(uuid.uuid4())

    user = UserDB(
        email=payload.email,
        name=payload.name,
        hashed_password=hashed,
        is_verified=False,
        verification_token=verification_token,
        role="CITIZEN",
        status="ACTIVE",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
def login_user(
    payload: UserLoginRequest, response: Response, db: Session = Depends(get_db)
) -> TokenResponse:
    user = db.query(UserDB).filter(UserDB.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is not active. Status: {user.status}",
        )

    access_token = create_access_token(user.id, user.email)
    refresh_token = create_refresh_token(user.id)

    # Set secure cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.ENV == "prod",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENV == "prod",
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user,
    )


@router.post("/logout")
def logout_user(response: Response) -> dict[str, str]:
    # Clear cookies
    response.delete_cookie(
        "access_token", secure=settings.ENV == "prod", samesite="lax"
    )
    response.delete_cookie(
        "refresh_token", secure=settings.ENV == "prod", samesite="lax"
    )
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=TokenResponse)
def refresh_session(
    request: Request,
    response: Response,
    payload: RefreshRequest | None = None,
    db: Session = Depends(get_db),
) -> TokenResponse:
    # 1. Extract refresh token from body or cookie
    token = None
    if payload and payload.refresh_token:
        token = payload.refresh_token
    if not token:
        token = request.cookies.get("refresh_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token missing"
        )

    try:
        decoded = decode_token(token)
        if decoded.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )
        user_id = decoded.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject"
            )
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
        ) from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        ) from e

    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    access_token = create_access_token(user.id, user.email)
    new_refresh_token = create_refresh_token(user.id)

    # Update cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.ENV == "prod",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=settings.ENV == "prod",
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=user,
    )


# Email Verification Skeletons
@router.post("/verify-email")
def verify_email(
    payload: VerifyEmailRequest, db: Session = Depends(get_db)
) -> dict[str, str]:
    user = db.query(UserDB).filter(UserDB.verification_token == payload.token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    user.is_verified = True
    user.verification_token = None
    db.commit()
    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
def resend_verification(
    payload: ForgotPasswordRequest, db: Session = Depends(get_db)
) -> dict[str, str]:
    # In production, this would send an email with the verification token
    user = db.query(UserDB).filter(UserDB.email == payload.email).first()
    if not user:
        # Avoid user enumeration by returning a success message even if email not found
        return {
            "message": "If the email is registered, verification link has been resent"
        }

    if user.is_verified:
        return {"message": "Email is already verified"}

    user.verification_token = str(uuid.uuid4())
    db.commit()
    # Return verification token in skeleton to make integration testing easy
    return {
        "message": "Verification link has been resent",
        "verification_token": user.verification_token,
    }


# Password Reset Skeletons
@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest, db: Session = Depends(get_db)
) -> dict[str, str]:
    # In production, this would generate reset token and email it
    user = db.query(UserDB).filter(UserDB.email == payload.email).first()
    if not user:
        return {
            "message": "If the email is registered, a password reset link has been sent"
        }

    user.reset_token = str(uuid.uuid4())
    db.commit()
    # Return reset token in skeleton to make integration testing easy
    return {
        "message": "Password reset link has been sent",
        "reset_token": user.reset_token,
    }


@router.post("/reset-password")
def reset_password(
    payload: ResetPasswordRequest, db: Session = Depends(get_db)
) -> dict[str, str]:
    user = db.query(UserDB).filter(UserDB.reset_token == payload.token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user.hashed_password = hash_password(payload.new_password)
    user.reset_token = None
    db.commit()
    return {"message": "Password has been reset successfully"}


@router.get("/me")
def get_me(current_user: UserDB = Depends(get_current_user)) -> dict[str, Any]:
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
    }


# Include the User Management routes
from .routes import router as user_router  # noqa: E402

router.include_router(user_router)
