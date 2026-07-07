import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, String

from helix_platform.persistence import Base


class UserDB(Base):
    """SQLAlchemy model representing a persistent User for Auth & Profile Identity."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(255), unique=True, index=True, nullable=True)
    name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        String(50), nullable=False, default="CITIZEN"
    )  # CITIZEN, OFFICER, MLA, ADMINISTRATOR
    status = Column(
        String(50), nullable=False, default="ACTIVE"
    )  # ACTIVE, PENDING_APPROVAL, DEACTIVATED, REJECTED
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True)
    reset_token = Column(String(255), nullable=True)
    department_id = Column(String(36), nullable=True)  # Applicable for Officer
    phone = Column(String(50), nullable=True)
    bio = Column(String(1024), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.UTC), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )


class InvitationDB(Base):
    """SQLAlchemy model for User Invitations."""

    __tablename__ = "invitations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # MLA, OFFICER
    department_id = Column(String(36), nullable=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    status = Column(
        String(50), nullable=False, default="PENDING"
    )  # PENDING, ACCEPTED, EXPIRED
    invited_by = Column(String(36), nullable=False)  # User ID of the inviter
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    expires_at = Column(DateTime, nullable=False)
