import datetime
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from helix_platform.persistence import get_db
from helix_platform.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from services.identity.models import InvitationDB, UserDB
from services.identity.schemas import (
    CitizenRegister,
    InvitationAccept,
    InvitationCreate,
    InvitationResponse,
    LoginRequest,
    TokenResponse,
    UserResponse,
    UserUpdate,
)

router = APIRouter(tags=["User Management"])


# Helper dependency to get current user from token or X-User-ID header
def get_current_user(
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
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
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
            detail="Missing or invalid Authorization header",
        )

    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is not active. Status: {user.status}",
        )
    return user


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

    user = UserDB(
        id=str(uuid.uuid4()),
        email=payload.email,
        name=payload.name,
        hashed_password=hash_password(payload.password),
        role="CITIZEN",
        status="ACTIVE",
        phone=payload.phone,
        bio=payload.bio,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is not active. Status: {user.status}",
        )

    access_token = create_access_token(data={"sub": user.id, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


# Profile Endpoints
@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: UserDB = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_profile(
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
    db.commit()
    db.refresh(current_user)
    return current_user


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
    # Authorization rules:
    # 1. System Administrator can invite anyone (MLAs or Officers)
    # 2. MLA can invite Officers
    if current_user.role == "ADMINISTRATOR":
        if payload.role not in ["MLA", "OFFICER"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Administrators can only invite MLAs or Officers",
            )
    elif current_user.role == "MLA":
        if payload.role != "OFFICER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MLAs can only invite Officers",
            )
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

    # Create the user with status PENDING_APPROVAL
    user = UserDB(
        id=str(uuid.uuid4()),
        email=invitation.email,
        name=payload.name,
        hashed_password=hash_password(payload.password),
        role=invitation.role,
        status="PENDING_APPROVAL",
        department_id=invitation.department_id,
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
            detail=f"User is not in PENDING_APPROVAL status. Current status: {target_user.status}",  # noqa: E501,  # noqa: E501
        )

    # Authorization rules:
    # 1. System Administrator can approve anyone (MLAs or Officers)
    # 2. MLA can approve Officers
    if current_user.role == "ADMINISTRATOR":
        pass
    elif current_user.role == "MLA":
        if target_user.role != "OFFICER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MLAs can only approve Officers",
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
            detail=f"User is not in PENDING_APPROVAL status. Current status: {target_user.status}",  # noqa: E501,  # noqa: E501
        )

    # Authorization rules: same as approval
    if current_user.role == "ADMINISTRATOR":
        pass
    elif current_user.role == "MLA":
        if target_user.role != "OFFICER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MLAs can only reject Officers",
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
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Only Admin, MLA, and Officer can view users list
    if current_user.role not in ["ADMINISTRATOR", "MLA", "OFFICER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view user list",
        )

    query = db.query(UserDB)
    if role:
        query = query.filter(UserDB.role == role)
    if status:
        query = query.filter(UserDB.status == status)
    return query.all()


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Self check or role check
    if current_user.id != user_id and current_user.role not in [
        "ADMINISTRATOR",
        "MLA",
        "OFFICER",
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
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    payload: UserUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Only Admin can update other users, or self-update
    if current_user.id != user_id and current_user.role != "ADMINISTRATOR":
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
    if payload.department_id is not None:
        # Only admin or MLA can set department for Officer
        if current_user.role not in ["ADMINISTRATOR", "MLA"]:
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
    if current_user.role != "ADMINISTRATOR":
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
