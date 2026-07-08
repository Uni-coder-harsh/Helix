import datetime
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from helix_platform.persistence import get_db
from helix_platform.security import (
    create_access_token,
    decode_access_token,
    get_user_permissions,
    hash_password,
    normalize_role,
    verify_password,
)
from services.identity.jurisdiction import (
    lookup_jurisdiction,
    validate_geojson_polygon,
)
from services.identity.models import (
    AssemblyConstituencyDB,
    AuditLoginDB,
    ConstituencyDB,
    CountryDB,
    DistrictDB,
    InvitationDB,
    ParliamentaryConstituencyDB,
    PasswordResetDB,
    RefreshTokenDB,
    SessionDB,
    StateDB,
    UserDB,
    VillageDB,
    WardDB,
)
from services.identity.schemas import (
    AssemblyConstituencyCreate,
    AssemblyConstituencyResponse,
    AssemblyConstituencyUpdate,
    AuditLoginResponse,
    BoundaryUploadRequest,
    ChangePasswordRequest,
    CitizenRegister,
    ConstituencyCreate,
    ConstituencyResponse,
    CountryCreate,
    CountryResponse,
    CountryUpdate,
    DistrictCreate,
    DistrictResponse,
    DistrictUpdate,
    ForgotPasswordRequest,
    InvitationAccept,
    InvitationCreate,
    InvitationResponse,
    JurisdictionLookupResponse,
    LoginRequest,
    ParliamentaryConstituencyCreate,
    ParliamentaryConstituencyResponse,
    ParliamentaryConstituencyUpdate,
    RefreshRequest,
    ResetPasswordRequest,
    SessionResponse,
    StateCreate,
    StateResponse,
    StateUpdate,
    TokenResponse,
    UserResponse,
    UserUpdate,
    VerifyEmailRequest,
    VillageCreate,
    VillageResponse,
    VillageUpdate,
    WardCreate,
    WardResponse,
    WardUpdate,
)

router = APIRouter(prefix="/identity", tags=["User Management"])


@router.get("")
@router.get("/")
def get_root() -> dict[str, str]:
    """Identity Service status endpoint."""
    return {"service": "Identity Service", "status": "active"}


# Helper dependency to get current user from token or X-User-ID header
def get_current_user(
    request: Request,
    authorization: str | None = Header(None),
    x_user_id: str | None = Header(None),
    db: Session = Depends(get_db),
) -> UserDB:
    user = None
    if x_user_id:
        user = db.query(UserDB).filter(UserDB.id == x_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found from X-User-ID header",
            )
    else:
        # Fallback to cookie if Authorization header is not set
        token = None
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        if not token:
            token = request.cookies.get("access_token")

        if token:
            try:
                payload = decode_access_token(token)
                user_id = payload.get("sub") or payload.get("user_id")
                if not user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token payload",
                    )
                user = db.query(UserDB).filter(UserDB.id == user_id).first()
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found",
                    )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Token validation failed: {e!s}",
                ) from e
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authentication credentials",
            )

    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is not active. Status: {user.status}",
        )
    return user


# Helper to enforce dynamic permissions on UserDB instances
def check_permission(user: UserDB, required_permission: str) -> None:
    perms = get_user_permissions(user.role)
    if required_permission not in perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: required permission '{required_permission}' not found for role '{user.role}'",
        )


def validate_geojson_or_400(geojson_boundary: str) -> None:
    try:
        validate_geojson_polygon(geojson_boundary)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


def get_entity_or_404(
    db: Session, model: object, entity_id: str, detail: str
) -> object:
    entity = db.query(model).filter(model.id == entity_id).first()
    if entity:
        return entity
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def resolve_assembly_constituency_id(
    assembly_constituency_id: str | None,
    constituency_id: str | None,
) -> str:
    resolved_id = assembly_constituency_id or constituency_id
    if resolved_id:
        return resolved_id
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="assembly_constituency_id or constituency_id must be provided",
    )


# Public Endpoints
@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register_citizen(payload: CitizenRegister, db: Session = Depends(get_db)):
    # Check if email is already taken
    existing_user = db.query(UserDB).filter(UserDB.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Validate Constituency if provided
    if payload.constituency_id:
        constituency = (
            db.query(ConstituencyDB)
            .filter(ConstituencyDB.id == payload.constituency_id)
            .first()
        )
        if not constituency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Constituency not found",
            )

    verification_token = str(uuid.uuid4())

    user = UserDB(
        id=str(uuid.uuid4()),
        email=payload.email,
        name=payload.name,
        hashed_password=hash_password(payload.password),
        role="Citizen",
        status="ACTIVE",
        is_verified=False,
        verification_token=verification_token,
        phone=payload.phone,
        bio=payload.bio,
        state_id=payload.state_id,
        district_id=payload.district_id,
        constituency_id=payload.constituency_id,
        ward_or_village=payload.ward_or_village,
        address=payload.address,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    user = db.query(UserDB).filter(UserDB.email == payload.email).first()
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")

    # Rate limiting & Lockout checks
    if (
        user
        and user.locked_until
        and user.locked_until > datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    ):
        audit_log = AuditLoginDB(
            id=str(uuid.uuid4()),
            user_id=user.id,
            email=payload.email,
            event_type="LOCKOUT",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(audit_log)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is temporarily locked. Try again after {user.locked_until.isoformat()}",
        )

    if not user or not verify_password(payload.password, user.hashed_password):
        if user:
            user.login_attempts += 1
            if user.login_attempts >= 5:
                user.locked_until = datetime.datetime.now(
                    datetime.UTC
                ) + datetime.timedelta(minutes=15)
                user.login_attempts = 0
            db.commit()

        audit_log = AuditLoginDB(
            id=str(uuid.uuid4()),
            user_id=user.id if user else None,
            email=payload.email,
            event_type="LOGIN_FAILED",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(audit_log)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if user.status != "ACTIVE":
        audit_log = AuditLoginDB(
            id=str(uuid.uuid4()),
            user_id=user.id,
            email=payload.email,
            event_type="LOGIN_FAILED",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(audit_log)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is not active. Status: {user.status}",
        )

    # Success: Reset attempts
    user.login_attempts = 0
    user.locked_until = None

    # Track active session
    session_expiry = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)
    session = SessionDB(
        id=str(uuid.uuid4()),
        user_id=user.id,
        device_info=user_agent[:255] if user_agent else None,
        ip_address=ip_address,
        is_active=True,
        expires_at=session_expiry,
    )
    db.add(session)

    # Rotate refresh token
    refresh_expiry = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)
    refresh_token_str = str(uuid.uuid4())
    refresh_token = RefreshTokenDB(
        id=str(uuid.uuid4()),
        user_id=user.id,
        token=refresh_token_str,
        is_revoked=False,
        expires_at=refresh_expiry,
    )
    db.add(refresh_token)

    audit_log = AuditLoginDB(
        id=str(uuid.uuid4()),
        user_id=user.id,
        email=user.email,
        event_type="LOGIN_SUCCESS",
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(audit_log)
    db.commit()

    access_token = create_access_token(data={"sub": user.id, "role": user.role})

    # Set access token and refresh token cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=24 * 60 * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token_str,
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/logout")
def logout(response: Response):
    # Clear cookies
    response.delete_cookie("access_token", samesite="lax")
    response.delete_cookie("refresh_token", samesite="lax")
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    request: Request,
    response: Response,
    payload: RefreshRequest | None = None,
    db: Session = Depends(get_db),
):
    token = None
    if payload and payload.refresh_token:
        token = payload.refresh_token
    if not token:
        token = request.cookies.get("refresh_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token missing"
        )

    # Validate refresh token from database
    db_token = (
        db.query(RefreshTokenDB)
        .filter(
            RefreshTokenDB.token == token,
            RefreshTokenDB.is_revoked.is_(False),
        )
        .first()
    )
    if not db_token or db_token.expires_at < datetime.datetime.now(
        datetime.UTC
    ).replace(tzinfo=None):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user = db.query(UserDB).filter(UserDB.id == db_token.user_id).first()
    if not user or user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Access Token Creation
    access_token = create_access_token(data={"sub": user.id, "role": user.role})

    # Token rotation: revoke old token and generate new one
    db_token.is_revoked = True

    new_token_str = str(uuid.uuid4())
    new_expiry = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)
    new_db_token = RefreshTokenDB(
        id=str(uuid.uuid4()),
        user_id=user.id,
        token=new_token_str,
        is_revoked=False,
        expires_at=new_expiry,
    )
    db.add(new_db_token)
    db.commit()

    # Update cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=24 * 60 * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=new_token_str,
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )

    return {
        "access_token": access_token,
        "refresh_token": new_token_str,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/verify-email")
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
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
def resend_verification(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == payload.email).first()
    if not user:
        return {
            "message": "If the email is registered, verification link has been resent"
        }

    if user.is_verified:
        return {"message": "Email is already verified"}

    user.verification_token = str(uuid.uuid4())
    db.commit()
    return {
        "message": "Verification link has been resent",
        "verification_token": user.verification_token,
    }


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == payload.email).first()
    if not user:
        return {
            "message": "If the email is registered, a password reset link has been sent"
        }

    reset_token = str(uuid.uuid4())
    expiry = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)

    db_reset = PasswordResetDB(
        id=str(uuid.uuid4()),
        user_id=user.id,
        token=reset_token,
        is_used=False,
        expires_at=expiry,
    )
    db.add(db_reset)
    db.commit()

    return {
        "message": "Password reset link has been sent",
        "reset_token": reset_token,
    }


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset_entry = (
        db.query(PasswordResetDB)
        .filter(
            PasswordResetDB.token == payload.token,
            PasswordResetDB.is_used.is_(False),
        )
        .first()
    )

    if not reset_entry or reset_entry.expires_at < datetime.datetime.now(
        datetime.UTC
    ).replace(tzinfo=None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user = db.query(UserDB).filter(UserDB.id == reset_entry.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Secure reset: update password and invalidate token
    user.hashed_password = hash_password(payload.new_password)
    reset_entry.is_used = True

    # Revoke all sessions for security upon password reset
    db.query(SessionDB).filter(SessionDB.user_id == user.id).update(
        {"is_active": False}
    )
    db.query(RefreshTokenDB).filter(RefreshTokenDB.user_id == user.id).update(
        {"is_revoked": True}
    )

    db.commit()
    return {"message": "Password has been reset successfully"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserDB = Depends(get_current_user)):
    return current_user


# Profile Endpoints
@router.get("/profile", response_model=UserResponse)
def get_profile_data(current_user: UserDB = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_profile_data(
    payload: UserUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.name is not None:
        current_user.name = payload.name
    if payload.phone is not None:
        current_user.phone = payload.phone
    if payload.bio is not None:
        current_user.bio = payload.bio
    if payload.state_id is not None:
        current_user.state_id = payload.state_id
    if payload.district_id is not None:
        current_user.district_id = payload.district_id
    if payload.constituency_id is not None:
        current_user.constituency_id = payload.constituency_id
    if payload.ward_or_village is not None:
        current_user.ward_or_village = payload.ward_or_village
    if payload.address is not None:
        current_user.address = payload.address
    db.commit()
    db.refresh(current_user)
    return current_user


# Session Auditing & Revocation APIs
@router.get("/sessions", response_model=list[SessionResponse])
def list_sessions(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(SessionDB)
        .filter(
            SessionDB.user_id == current_user.id,
            SessionDB.is_active,
            SessionDB.expires_at
            > datetime.datetime.now(datetime.UTC).replace(tzinfo=None),
        )
        .all()
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_active_session(
    session_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = (
        db.query(SessionDB)
        .filter(SessionDB.id == session_id, SessionDB.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    session.is_active = False
    db.commit()
    return


@router.post("/sessions/logout-all", status_code=status.HTTP_204_NO_CONTENT)
def logout_all_sessions(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Deactivate all active sessions for user
    db.query(SessionDB).filter(SessionDB.user_id == current_user.id).update(
        {"is_active": False}
    )
    # Revoke all refresh tokens
    db.query(RefreshTokenDB).filter(RefreshTokenDB.user_id == current_user.id).update(
        {"is_revoked": True}
    )
    db.commit()
    return


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password",
        )
    current_user.hashed_password = hash_password(payload.new_password)
    # Revoke other sessions for security on password change
    db.query(SessionDB).filter(SessionDB.user_id == current_user.id).update(
        {"is_active": False}
    )
    db.query(RefreshTokenDB).filter(RefreshTokenDB.user_id == current_user.id).update(
        {"is_revoked": True}
    )
    db.commit()
    return {"message": "Password changed successfully"}


# Geography API Router (Multi-Tenancy Setup)
@router.post(
    "/countries", response_model=CountryResponse, status_code=status.HTTP_201_CREATED
)
def add_country(
    payload: CountryCreate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    country = CountryDB(
        id=str(uuid.uuid4()),
        name=payload.name,
        code=payload.code,
        is_active=True,
    )
    db.add(country)
    db.commit()
    db.refresh(country)
    return country


@router.get("/countries", response_model=list[CountryResponse])
def list_countries(
    include_inactive: bool = False,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    query = db.query(CountryDB)
    if not include_inactive:
        query = query.filter(CountryDB.is_active.is_(True))
    return query.order_by(CountryDB.name.asc()).all()


@router.get("/countries/{country_id}", response_model=CountryResponse)
def get_country(
    country_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    return get_entity_or_404(db, CountryDB, country_id, "Country not found")


@router.put("/countries/{country_id}", response_model=CountryResponse)
def update_country(
    country_id: str,
    payload: CountryUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    country = get_entity_or_404(db, CountryDB, country_id, "Country not found")

    if payload.name is not None:
        country.name = payload.name
    if payload.code is not None:
        country.code = payload.code
    if payload.is_active is not None:
        country.is_active = payload.is_active

    db.commit()
    db.refresh(country)
    return country


@router.delete("/countries/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(
    country_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    country = get_entity_or_404(db, CountryDB, country_id, "Country not found")
    country.is_active = False
    db.commit()
    return


@router.post(
    "/states", response_model=StateResponse, status_code=status.HTTP_201_CREATED
)
def add_state(
    payload: StateCreate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    get_entity_or_404(db, CountryDB, payload.country_id, "Country not found")
    state = StateDB(
        id=str(uuid.uuid4()),
        name=payload.name,
        country_id=payload.country_id,
        code=payload.code,
        is_active=True,
    )
    db.add(state)
    db.commit()
    db.refresh(state)
    return state


@router.get("/states", response_model=list[StateResponse])
def list_states(
    country_id: str | None = None,
    include_inactive: bool = False,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    query = db.query(StateDB)
    if country_id:
        query = query.filter(StateDB.country_id == country_id)
    if not include_inactive:
        query = query.filter(StateDB.is_active.is_(True))
    return query.order_by(StateDB.name.asc()).all()


@router.get("/states/{state_id}", response_model=StateResponse)
def get_state(
    state_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    return get_entity_or_404(db, StateDB, state_id, "State not found")


@router.put("/states/{state_id}", response_model=StateResponse)
def update_state(
    state_id: str,
    payload: StateUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    state = get_entity_or_404(db, StateDB, state_id, "State not found")

    if payload.country_id is not None:
        get_entity_or_404(db, CountryDB, payload.country_id, "Country not found")
        state.country_id = payload.country_id
    if payload.name is not None:
        state.name = payload.name
    if payload.code is not None:
        state.code = payload.code
    if payload.is_active is not None:
        state.is_active = payload.is_active

    db.commit()
    db.refresh(state)
    return state


@router.delete("/states/{state_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_state(
    state_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    state = get_entity_or_404(db, StateDB, state_id, "State not found")
    state.is_active = False
    db.commit()
    return


@router.post(
    "/districts", response_model=DistrictResponse, status_code=status.HTTP_201_CREATED
)
def add_district(
    payload: DistrictCreate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    get_entity_or_404(db, StateDB, payload.state_id, "State not found")
    district = DistrictDB(
        id=str(uuid.uuid4()),
        name=payload.name,
        state_id=payload.state_id,
        code=payload.code,
        is_active=True,
    )
    db.add(district)
    db.commit()
    db.refresh(district)
    return district


@router.get("/districts", response_model=list[DistrictResponse])
def list_districts(
    state_id: str | None = None,
    include_inactive: bool = False,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    query = db.query(DistrictDB)
    if state_id:
        query = query.filter(DistrictDB.state_id == state_id)
    if not include_inactive:
        query = query.filter(DistrictDB.is_active.is_(True))
    return query.order_by(DistrictDB.name.asc()).all()


@router.get("/districts/{district_id}", response_model=DistrictResponse)
def get_district(
    district_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    return get_entity_or_404(db, DistrictDB, district_id, "District not found")


@router.put("/districts/{district_id}", response_model=DistrictResponse)
def update_district(
    district_id: str,
    payload: DistrictUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    district = get_entity_or_404(db, DistrictDB, district_id, "District not found")

    if payload.state_id is not None:
        get_entity_or_404(db, StateDB, payload.state_id, "State not found")
        district.state_id = payload.state_id
    if payload.name is not None:
        district.name = payload.name
    if payload.code is not None:
        district.code = payload.code
    if payload.is_active is not None:
        district.is_active = payload.is_active

    db.commit()
    db.refresh(district)
    return district


@router.delete("/districts/{district_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_district(
    district_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    district = get_entity_or_404(db, DistrictDB, district_id, "District not found")
    district.is_active = False
    db.commit()
    return


@router.post(
    "/constituencies",
    response_model=ConstituencyResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_constituency(
    payload: ConstituencyCreate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    get_entity_or_404(db, DistrictDB, payload.district_id, "District not found")
    if payload.parliamentary_constituency_id is not None:
        get_entity_or_404(
            db,
            ParliamentaryConstituencyDB,
            payload.parliamentary_constituency_id,
            "Parliamentary Constituency not found",
        )
    if payload.geojson_boundary:
        validate_geojson_or_400(payload.geojson_boundary)

    constituency = ConstituencyDB(
        id=str(uuid.uuid4()),
        name=payload.name,
        district_id=payload.district_id,
        parliamentary_constituency_id=payload.parliamentary_constituency_id,
        code=payload.code,
        geojson_boundary=payload.geojson_boundary,
        area_metadata=payload.area_metadata,
        population_metadata=payload.population_metadata,
        is_active=True,
        status="ACTIVE",
    )
    db.add(constituency)
    db.commit()
    db.refresh(constituency)
    return constituency


@router.get("/constituencies", response_model=list[ConstituencyResponse])
def list_constituencies(
    district_id: str | None = None,
    parliamentary_constituency_id: str | None = None,
    include_inactive: bool = False,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    query = db.query(ConstituencyDB)
    if district_id:
        query = query.filter(ConstituencyDB.district_id == district_id)
    if parliamentary_constituency_id:
        query = query.filter(
            ConstituencyDB.parliamentary_constituency_id
            == parliamentary_constituency_id
        )
    if not include_inactive:
        query = query.filter(ConstituencyDB.is_active.is_(True))
    return query.order_by(ConstituencyDB.name.asc()).all()


@router.post(
    "/constituencies/{constituency_id}/assign-mla", response_model=ConstituencyResponse
)
def assign_mla_constituency(
    constituency_id: str,
    mla_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    constituency = get_entity_or_404(
        db,
        ConstituencyDB,
        constituency_id,
        "Constituency not found",
    )

    mla = db.query(UserDB).filter(UserDB.id == mla_id, UserDB.role == "MLA").first()
    if not mla:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MLA user not found or user role is not MLA",
        )

    prev_constituency = (
        db.query(ConstituencyDB).filter(ConstituencyDB.mla_id == mla_id).first()
    )
    if prev_constituency:
        prev_constituency.mla_id = None

    constituency.mla_id = mla.id
    mla.constituency_id = constituency.id
    db.commit()
    db.refresh(constituency)
    return constituency


@router.post(
    "/constituencies/{constituency_id}/geojson", response_model=ConstituencyResponse
)
def update_constituency_geojson(
    constituency_id: str,
    geojson_boundary: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    constituency = get_entity_or_404(
        db,
        ConstituencyDB,
        constituency_id,
        "Constituency not found",
    )
    validate_geojson_or_400(geojson_boundary)

    constituency.geojson_boundary = geojson_boundary
    constituency.boundary_version += 1
    db.commit()
    db.refresh(constituency)
    return constituency


@router.post("/wards", response_model=WardResponse, status_code=status.HTTP_201_CREATED)
def add_ward(
    payload: WardCreate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    assembly_constituency_id = resolve_assembly_constituency_id(
        payload.assembly_constituency_id,
        payload.constituency_id,
    )
    get_entity_or_404(
        db,
        AssemblyConstituencyDB,
        assembly_constituency_id,
        "Assembly Constituency not found",
    )
    if payload.geojson_boundary:
        validate_geojson_or_400(payload.geojson_boundary)

    ward = WardDB(
        id=str(uuid.uuid4()),
        name=payload.name,
        assembly_constituency_id=assembly_constituency_id,
        code=payload.code,
        geojson_boundary=payload.geojson_boundary,
        is_active=True,
    )
    db.add(ward)
    db.commit()
    db.refresh(ward)
    return ward


@router.get("/wards", response_model=list[WardResponse])
def list_wards(
    assembly_constituency_id: str | None = None,
    constituency_id: str | None = None,
    include_inactive: bool = False,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    query = db.query(WardDB)
    resolved_id = assembly_constituency_id or constituency_id
    if resolved_id:
        query = query.filter(WardDB.assembly_constituency_id == resolved_id)
    if not include_inactive:
        query = query.filter(WardDB.is_active.is_(True))
    return query.order_by(WardDB.name.asc()).all()


# User Audit Logs Route
@router.get("/audit-logins", response_model=list[AuditLoginResponse])
def list_audit_logins(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    return db.query(AuditLoginDB).order_by(AuditLoginDB.timestamp.desc()).all()


# Invitation Workflow
@router.post(
    "/invitations",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invitation(
    payload: InvitationCreate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Normalize role
    normalized = normalize_role(payload.role)
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {payload.role}",
        )
    payload.role = normalized

    # Authorization rules:
    # 1. System Administrator can invite anyone (MLAs or Officers)
    # 2. MLA can invite Officers to their own constituency

    if current_user.role == "System Administrator":
        if payload.role not in ["MLA", "Officer"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Administrators can only invite MLAs or Officers",
            )
    elif current_user.role == "MLA":
        if payload.role != "Officer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MLAs can only invite Officers",
            )
        # Force tenancy to the MLA's constituency
        payload.constituency_id = current_user.constituency_id
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators and MLAs can invite other users",
        )

    # Check if user already exists
    existing_user = db.query(UserDB).filter(UserDB.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Generate a unique token
    token = str(uuid.uuid4())
    expires_at = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)

    invitation = InvitationDB(
        id=str(uuid.uuid4()),
        email=payload.email,
        role=payload.role,
        department_id=payload.department_id,
        constituency_id=payload.constituency_id,
        token=token,
        status="PENDING",
        invited_by=current_user.id,
        expires_at=expires_at,
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation


@router.post("/invitations/accept", response_model=UserResponse)
def accept_invitation(payload: InvitationAccept, db: Session = Depends(get_db)):
    invitation = (
        db.query(InvitationDB).filter(InvitationDB.token == payload.token).first()
    )
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation token not found",
        )

    if invitation.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invitation status is {invitation.status}",
        )

    if invitation.expires_at.replace(tzinfo=datetime.UTC) < datetime.datetime.now(
        datetime.UTC
    ):
        invitation.status = "EXPIRED"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation token has expired",
        )

    # Check if user already exists
    existing_user = db.query(UserDB).filter(UserDB.email == invitation.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Fetch constituency and district/state to populate geographic profile of the user
    state_id = None
    district_id = None
    if invitation.constituency_id:
        constituency = (
            db.query(ConstituencyDB)
            .filter(ConstituencyDB.id == invitation.constituency_id)
            .first()
        )
        if constituency:
            district_id = constituency.district_id
            district = db.query(DistrictDB).filter(DistrictDB.id == district_id).first()
            if district:
                state_id = district.state_id

    # Create the user with status PENDING_APPROVAL
    user = UserDB(
        id=str(uuid.uuid4()),
        email=invitation.email,
        name=payload.name,
        hashed_password=hash_password(payload.password),
        role=invitation.role,
        status="PENDING_APPROVAL",
        department_id=invitation.department_id,
        constituency_id=invitation.constituency_id,
        district_id=district_id,
        state_id=state_id,
        phone=payload.phone,
        bio=payload.bio,
    )
    db.add(user)

    # Mark invitation as accepted
    invitation.status = "ACCEPTED"

    db.commit()
    db.refresh(user)
    return user


# User Approval Status
@router.post("/users/{user_id}/approve", response_model=UserResponse)
def approve_user(
    user_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if target_user.status != "PENDING_APPROVAL":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User is not in PENDING_APPROVAL status. Current status: {target_user.status}",
        )

    # Authorization rules:
    # 1. System Administrator can approve anyone (MLAs or Officers)
    # 2. MLA can approve Officers in their own constituency

    if current_user.role == "System Administrator":
        pass
    elif current_user.role == "MLA":
        if target_user.role != "Officer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MLAs can only approve Officers",
            )
        if target_user.constituency_id != current_user.constituency_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MLAs can only approve Officers assigned to their constituency",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators and MLAs can approve users",
        )

    target_user.status = "ACTIVE"
    db.commit()
    db.refresh(target_user)
    return target_user


@router.post("/users/{user_id}/reject", response_model=UserResponse)
def reject_user(
    user_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if target_user.status != "PENDING_APPROVAL":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User is not in PENDING_APPROVAL status. Current status: {target_user.status}",
        )

    # Authorization rules
    if current_user.role == "System Administrator":
        pass
    elif current_user.role == "MLA":
        if target_user.role != "Officer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MLAs can only reject Officers",
            )
        if target_user.constituency_id != current_user.constituency_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MLAs can only reject Officers assigned to their constituency",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators and MLAs can reject users",
        )

    target_user.status = "REJECTED"
    db.commit()
    db.refresh(target_user)
    return target_user


# User CRUD
@router.get("/users", response_model=list[UserResponse])
def list_users(
    role: str | None = None,
    status: str | None = None,
    constituency_id: str | None = None,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Only Admin, MLA, and Officer can view users list
    if current_user.role not in ["System Administrator", "MLA", "Officer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view user list",
        )

    query = db.query(UserDB)
    if role:
        query = query.filter(UserDB.role == role)
    if status:
        query = query.filter(UserDB.status == status)
    if constituency_id:
        query = query.filter(UserDB.constituency_id == constituency_id)

    # Tenant Filtering: MLA and Officer can only list users within their own constituency
    if current_user.role in ["MLA", "Officer"]:
        query = query.filter(UserDB.constituency_id == current_user.constituency_id)

    return query.all()


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Self check or role check
    if current_user.id != user_id and current_user.role not in [
        "System Administrator",
        "MLA",
        "Officer",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user",
        )

    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Tenant Isolation: MLA / Officer cannot view users from other constituencies
    if (
        current_user.role in ["MLA", "Officer"]
        and user.constituency_id != current_user.constituency_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view users from outside your constituency",
        )

    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    payload: UserUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Only Admin can update other users, or self-update
    if current_user.id != user_id and current_user.role != "System Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators can edit other users",
        )

    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if payload.name is not None:
        user.name = payload.name
    if payload.phone is not None:
        user.phone = payload.phone
    if payload.bio is not None:
        user.bio = payload.bio
    if payload.state_id is not None:
        user.state_id = payload.state_id
    if payload.district_id is not None:
        user.district_id = payload.district_id
    if payload.constituency_id is not None:
        user.constituency_id = payload.constituency_id
    if payload.ward_or_village is not None:
        user.ward_or_village = payload.ward_or_village
    if payload.address is not None:
        user.address = payload.address

    if payload.department_id is not None:
        # Only admin or MLA can set department for Officer
        if current_user.role not in ["System Administrator", "MLA"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to set department_id",
            )
        user.department_id = payload.department_id

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "System Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators can delete users",
        )

    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Soft delete: set status to DEACTIVATED
    user.status = "DEACTIVATED"
    db.commit()
    return


# Jurisdiction Lookup Endpoint
@router.get("/jurisdiction/lookup", response_model=JurisdictionLookupResponse)
def lookup_jurisdiction_coords(
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db),
):
    """Given GPS coordinates (latitude and longitude), return State, District,
    Parliamentary/Assembly Constituencies, and Ward/Village containing the coordinates.
    """
    return lookup_jurisdiction(db, latitude, longitude)


# Parliamentary Constituency CRUD
@router.post(
    "/parliamentary-constituencies",
    response_model=ParliamentaryConstituencyResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_parliamentary_constituency(
    payload: ParliamentaryConstituencyCreate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    get_entity_or_404(db, StateDB, payload.state_id, "State not found")
    if payload.geojson_boundary:
        validate_geojson_or_400(payload.geojson_boundary)

    pc = ParliamentaryConstituencyDB(
        id=str(uuid.uuid4()),
        name=payload.name,
        state_id=payload.state_id,
        code=payload.code,
        geojson_boundary=payload.geojson_boundary,
        area_metadata=payload.area_metadata,
        population_metadata=payload.population_metadata,
        is_active=True,
    )
    db.add(pc)
    db.commit()
    db.refresh(pc)
    return pc


@router.get(
    "/parliamentary-constituencies",
    response_model=list[ParliamentaryConstituencyResponse],
)
def list_parliamentary_constituencies(
    state_id: str | None = None,
    include_inactive: bool = False,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    query = db.query(ParliamentaryConstituencyDB)
    if state_id:
        query = query.filter(ParliamentaryConstituencyDB.state_id == state_id)
    if not include_inactive:
        query = query.filter(ParliamentaryConstituencyDB.is_active.is_(True))
    return query.order_by(ParliamentaryConstituencyDB.name.asc()).all()


@router.get(
    "/parliamentary-constituencies/{pc_id}",
    response_model=ParliamentaryConstituencyResponse,
)
def get_parliamentary_constituency(
    pc_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    return get_entity_or_404(
        db,
        ParliamentaryConstituencyDB,
        pc_id,
        "Parliamentary Constituency not found",
    )


@router.put(
    "/parliamentary-constituencies/{pc_id}",
    response_model=ParliamentaryConstituencyResponse,
)
def update_parliamentary_constituency(
    pc_id: str,
    payload: ParliamentaryConstituencyUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    pc = get_entity_or_404(
        db,
        ParliamentaryConstituencyDB,
        pc_id,
        "Parliamentary Constituency not found",
    )

    if payload.name is not None:
        pc.name = payload.name
    if payload.state_id is not None:
        get_entity_or_404(db, StateDB, payload.state_id, "State not found")
        pc.state_id = payload.state_id
    if payload.code is not None:
        pc.code = payload.code
    if payload.is_active is not None:
        pc.is_active = payload.is_active
    if payload.area_metadata is not None:
        pc.area_metadata = payload.area_metadata
    if payload.population_metadata is not None:
        pc.population_metadata = payload.population_metadata
    if payload.geojson_boundary is not None:
        validate_geojson_or_400(payload.geojson_boundary)
        pc.geojson_boundary = payload.geojson_boundary
        pc.boundary_version += 1

    db.commit()
    db.refresh(pc)
    return pc


@router.delete(
    "/parliamentary-constituencies/{pc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_parliamentary_constituency(
    pc_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    pc = get_entity_or_404(
        db,
        ParliamentaryConstituencyDB,
        pc_id,
        "Parliamentary Constituency not found",
    )
    pc.is_active = False
    db.commit()
    return


# Assembly Constituency CRUD
@router.post(
    "/assembly-constituencies",
    response_model=AssemblyConstituencyResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_assembly_constituency(
    payload: AssemblyConstituencyCreate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    get_entity_or_404(db, DistrictDB, payload.district_id, "District not found")
    if payload.parliamentary_constituency_id is not None:
        get_entity_or_404(
            db,
            ParliamentaryConstituencyDB,
            payload.parliamentary_constituency_id,
            "Parliamentary Constituency not found",
        )
    if payload.geojson_boundary:
        validate_geojson_or_400(payload.geojson_boundary)

    ac = AssemblyConstituencyDB(
        id=str(uuid.uuid4()),
        name=payload.name,
        district_id=payload.district_id,
        parliamentary_constituency_id=payload.parliamentary_constituency_id,
        code=payload.code,
        geojson_boundary=payload.geojson_boundary,
        area_metadata=payload.area_metadata,
        population_metadata=payload.population_metadata,
        is_active=True,
        status="ACTIVE",
    )
    db.add(ac)
    db.commit()
    db.refresh(ac)
    return ac


@router.get(
    "/assembly-constituencies",
    response_model=list[AssemblyConstituencyResponse],
)
def list_assembly_constituencies(
    district_id: str | None = None,
    parliamentary_constituency_id: str | None = None,
    include_inactive: bool = False,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    query = db.query(AssemblyConstituencyDB)
    if district_id:
        query = query.filter(AssemblyConstituencyDB.district_id == district_id)
    if parliamentary_constituency_id:
        query = query.filter(
            AssemblyConstituencyDB.parliamentary_constituency_id
            == parliamentary_constituency_id
        )
    if not include_inactive:
        query = query.filter(AssemblyConstituencyDB.is_active.is_(True))
    return query.order_by(AssemblyConstituencyDB.name.asc()).all()


@router.get(
    "/assembly-constituencies/{ac_id}",
    response_model=AssemblyConstituencyResponse,
)
def get_assembly_constituency(
    ac_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    return get_entity_or_404(
        db,
        AssemblyConstituencyDB,
        ac_id,
        "Assembly Constituency not found",
    )


@router.put(
    "/assembly-constituencies/{ac_id}",
    response_model=AssemblyConstituencyResponse,
)
def update_assembly_constituency(
    ac_id: str,
    payload: AssemblyConstituencyUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    ac = get_entity_or_404(
        db,
        AssemblyConstituencyDB,
        ac_id,
        "Assembly Constituency not found",
    )

    if payload.name is not None:
        ac.name = payload.name
    if payload.district_id is not None:
        get_entity_or_404(db, DistrictDB, payload.district_id, "District not found")
        ac.district_id = payload.district_id
    if payload.parliamentary_constituency_id is not None:
        get_entity_or_404(
            db,
            ParliamentaryConstituencyDB,
            payload.parliamentary_constituency_id,
            "Parliamentary Constituency not found",
        )
        ac.parliamentary_constituency_id = payload.parliamentary_constituency_id
    if payload.code is not None:
        ac.code = payload.code
    if payload.is_active is not None:
        ac.is_active = payload.is_active
        ac.status = "ACTIVE" if payload.is_active else "DEACTIVATED"
    if payload.area_metadata is not None:
        ac.area_metadata = payload.area_metadata
    if payload.population_metadata is not None:
        ac.population_metadata = payload.population_metadata
    if payload.geojson_boundary is not None:
        validate_geojson_or_400(payload.geojson_boundary)
        ac.geojson_boundary = payload.geojson_boundary
        ac.boundary_version += 1

    db.commit()
    db.refresh(ac)
    return ac


@router.delete(
    "/assembly-constituencies/{ac_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_assembly_constituency(
    ac_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    ac = get_entity_or_404(
        db,
        AssemblyConstituencyDB,
        ac_id,
        "Assembly Constituency not found",
    )
    ac.is_active = False
    ac.status = "DEACTIVATED"
    db.commit()
    return


# Extended Ward Endpoints
@router.get("/wards/{ward_id}", response_model=WardResponse)
def get_ward(
    ward_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    return get_entity_or_404(db, WardDB, ward_id, "Ward not found")


@router.put("/wards/{ward_id}", response_model=WardResponse)
def update_ward(
    ward_id: str,
    payload: WardUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    ward = get_entity_or_404(db, WardDB, ward_id, "Ward not found")

    if payload.name is not None:
        ward.name = payload.name
    if (
        payload.assembly_constituency_id is not None
        or payload.constituency_id is not None
    ):
        assembly_constituency_id = resolve_assembly_constituency_id(
            payload.assembly_constituency_id,
            payload.constituency_id,
        )
        get_entity_or_404(
            db,
            AssemblyConstituencyDB,
            assembly_constituency_id,
            "Assembly Constituency not found",
        )
        ward.assembly_constituency_id = assembly_constituency_id
    if payload.code is not None:
        ward.code = payload.code
    if payload.is_active is not None:
        ward.is_active = payload.is_active
    if payload.geojson_boundary is not None:
        validate_geojson_or_400(payload.geojson_boundary)
        ward.geojson_boundary = payload.geojson_boundary

    db.commit()
    db.refresh(ward)
    return ward


@router.delete("/wards/{ward_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ward(
    ward_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    ward = get_entity_or_404(db, WardDB, ward_id, "Ward not found")
    ward.is_active = False
    db.commit()
    return


# Village Endpoints
@router.post(
    "/villages", response_model=VillageResponse, status_code=status.HTTP_201_CREATED
)
def add_village(
    payload: VillageCreate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    assembly_constituency_id = resolve_assembly_constituency_id(
        payload.assembly_constituency_id,
        payload.constituency_id,
    )
    get_entity_or_404(
        db,
        AssemblyConstituencyDB,
        assembly_constituency_id,
        "Assembly Constituency not found",
    )
    if payload.geojson_boundary:
        validate_geojson_or_400(payload.geojson_boundary)

    village = VillageDB(
        id=str(uuid.uuid4()),
        name=payload.name,
        assembly_constituency_id=assembly_constituency_id,
        code=payload.code,
        geojson_boundary=payload.geojson_boundary,
        is_active=True,
    )
    db.add(village)
    db.commit()
    db.refresh(village)
    return village


@router.get("/villages", response_model=list[VillageResponse])
def list_villages(
    assembly_constituency_id: str | None = None,
    constituency_id: str | None = None,
    include_inactive: bool = False,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    query = db.query(VillageDB)
    resolved_id = assembly_constituency_id or constituency_id
    if resolved_id:
        query = query.filter(VillageDB.assembly_constituency_id == resolved_id)
    if not include_inactive:
        query = query.filter(VillageDB.is_active.is_(True))
    return query.order_by(VillageDB.name.asc()).all()


@router.get("/villages/{village_id}", response_model=VillageResponse)
def get_village(
    village_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    return get_entity_or_404(db, VillageDB, village_id, "Village not found")


@router.put("/villages/{village_id}", response_model=VillageResponse)
def update_village(
    village_id: str,
    payload: VillageUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    village = get_entity_or_404(db, VillageDB, village_id, "Village not found")

    if payload.name is not None:
        village.name = payload.name
    if (
        payload.assembly_constituency_id is not None
        or payload.constituency_id is not None
    ):
        assembly_constituency_id = resolve_assembly_constituency_id(
            payload.assembly_constituency_id,
            payload.constituency_id,
        )
        get_entity_or_404(
            db,
            AssemblyConstituencyDB,
            assembly_constituency_id,
            "Assembly Constituency not found",
        )
        village.assembly_constituency_id = assembly_constituency_id
    if payload.code is not None:
        village.code = payload.code
    if payload.is_active is not None:
        village.is_active = payload.is_active
    if payload.geojson_boundary is not None:
        validate_geojson_or_400(payload.geojson_boundary)
        village.geojson_boundary = payload.geojson_boundary

    db.commit()
    db.refresh(village)
    return village


@router.delete("/villages/{village_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_village(
    village_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    village = get_entity_or_404(db, VillageDB, village_id, "Village not found")
    village.is_active = False
    db.commit()
    return


# Boundary Upload/Replace Endpoints
@router.post(
    "/parliamentary-constituencies/{id}/boundary",
    response_model=ParliamentaryConstituencyResponse,
)
def replace_parliamentary_boundary(
    id: str,
    payload: BoundaryUploadRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    pc = get_entity_or_404(
        db,
        ParliamentaryConstituencyDB,
        id,
        "Parliamentary Constituency not found",
    )
    validate_geojson_or_400(payload.geojson_boundary)

    pc.geojson_boundary = payload.geojson_boundary
    pc.boundary_version += 1
    db.commit()
    db.refresh(pc)
    return pc


@router.post(
    "/assembly-constituencies/{id}/boundary",
    response_model=AssemblyConstituencyResponse,
)
def replace_assembly_boundary(
    id: str,
    payload: BoundaryUploadRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    ac = get_entity_or_404(
        db,
        AssemblyConstituencyDB,
        id,
        "Assembly Constituency not found",
    )
    validate_geojson_or_400(payload.geojson_boundary)

    ac.geojson_boundary = payload.geojson_boundary
    ac.boundary_version += 1
    db.commit()
    db.refresh(ac)
    return ac


@router.post("/wards/{id}/boundary", response_model=WardResponse)
def replace_ward_boundary(
    id: str,
    payload: BoundaryUploadRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    ward = get_entity_or_404(db, WardDB, id, "Ward not found")
    validate_geojson_or_400(payload.geojson_boundary)

    ward.geojson_boundary = payload.geojson_boundary
    db.commit()
    db.refresh(ward)
    return ward


@router.post("/villages/{id}/boundary", response_model=VillageResponse)
def replace_village_boundary(
    id: str,
    payload: BoundaryUploadRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_permission(current_user, "system:admin")
    village = get_entity_or_404(db, VillageDB, id, "Village not found")
    validate_geojson_or_400(payload.geojson_boundary)

    village.geojson_boundary = payload.geojson_boundary
    db.commit()
    db.refresh(village)
    return village
