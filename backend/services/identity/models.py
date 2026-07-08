import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from helix_platform.persistence import Base


class CountryDB(Base):
    """SQLAlchemy model representing a Country."""

    __tablename__ = "countries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), unique=True, nullable=False)


class StateDB(Base):
    """SQLAlchemy model representing a State."""

    __tablename__ = "states"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    country_id = Column(String(36), ForeignKey("countries.id"), nullable=False)


class DistrictDB(Base):
    """SQLAlchemy model representing a District."""

    __tablename__ = "districts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    state_id = Column(String(36), ForeignKey("states.id"), nullable=False)


class ConstituencyDB(Base):
    """SQLAlchemy model representing an Electoral Constituency with GeoJSON boundaries."""

    __tablename__ = "constituencies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    district_id = Column(String(36), ForeignKey("districts.id"), nullable=False)
    geojson_boundary = Column(Text, nullable=True)  # Store boundary as a GeoJSON string
    mla_id = Column(String(36), nullable=True)  # Reference to UserDB.id
    status = Column(String(50), nullable=False, default="ACTIVE")  # ACTIVE, DEACTIVATED
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.UTC), nullable=False
    )


class WardDB(Base):
    """SQLAlchemy model representing a Ward or local boundary within a constituency."""

    __tablename__ = "wards"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    constituency_id = Column(
        String(36), ForeignKey("constituencies.id"), nullable=False
    )


class UserDB(Base):
    """SQLAlchemy model representing a persistent User for Auth & Profile Identity."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(255), unique=True, index=True, nullable=True)
    name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        String(50), nullable=False, default="Citizen"
    )  # Citizen, Officer, MLA, MP, System Administrator
    status = Column(
        String(50), nullable=False, default="ACTIVE"
    )  # ACTIVE, PENDING_APPROVAL, DEACTIVATED, REJECTED
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True)
    reset_token = Column(String(255), nullable=True)
    department_id = Column(String(36), nullable=True)  # Applicable for Officer
    phone = Column(String(50), nullable=True)
    bio = Column(String(1024), nullable=True)

    # Geography Scope & Address
    state_id = Column(String(36), nullable=True)
    district_id = Column(String(36), nullable=True)
    constituency_id = Column(String(36), nullable=True)
    ward_or_village = Column(String(255), nullable=True)
    address = Column(String(1024), nullable=True)

    # Security Lockouts
    login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.UTC), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )


class SessionDB(Base):
    """SQLAlchemy model for active user sessions."""

    __tablename__ = "user_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    device_info = Column(String(255), nullable=True)
    ip_address = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    expires_at = Column(DateTime, nullable=False)


class RefreshTokenDB(Base):
    """SQLAlchemy model for rotated refresh tokens."""

    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    expires_at = Column(DateTime, nullable=False)


class PasswordResetDB(Base):
    """SQLAlchemy model for tracking password reset requests."""

    __tablename__ = "password_resets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    expires_at = Column(DateTime, nullable=False)


class AuditLoginDB(Base):
    """SQLAlchemy model for security audit logs on login/logout events."""

    __tablename__ = "audit_logins"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    email = Column(String(255), nullable=False)
    event_type = Column(
        String(50), nullable=False
    )  # LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT, LOCKOUT
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))


class RoleDB(Base):
    """SQLAlchemy model for dynamic RBAC roles."""

    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    parent_role_id = Column(String(36), ForeignKey("roles.id"), nullable=True)


class PermissionDB(Base):
    """SQLAlchemy model for dynamic RBAC permissions."""

    __tablename__ = "permissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)


class RolePermissionDB(Base):
    """Junction table for role-to-permission mapping."""

    __tablename__ = "role_permissions"

    role_id = Column(String(36), ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(String(36), ForeignKey("permissions.id"), primary_key=True)


class InvitationDB(Base):
    """SQLAlchemy model for User Invitations."""

    __tablename__ = "invitations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # MLA, OFFICER
    department_id = Column(String(36), nullable=True)
    constituency_id = Column(String(36), nullable=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    status = Column(
        String(50), nullable=False, default="PENDING"
    )  # PENDING, ACCEPTED, EXPIRED
    invited_by = Column(String(36), nullable=False)  # User ID of the inviter
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    expires_at = Column(DateTime, nullable=False)
