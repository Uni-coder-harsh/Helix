import datetime
import functools
import inspect
from collections.abc import Callable
from typing import Any

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from helix_platform.config import get_settings

security_scheme = HTTPBearer(auto_error=False)


def create_access_token(
    data: dict[str, Any], expires_delta: datetime.timedelta | None = None
) -> str:
    """Generates a cryptographically signed JWT access token."""
    settings = get_settings()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.datetime.now(datetime.UTC) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Decodes and verifies a JWT access token."""
    settings = get_settings()
    return jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )


def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a hashed bcrypt password."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


class Permissions:
    ISSUES_CREATE = "issues:create"
    ISSUES_READ = "issues:read"
    ISSUES_LIST_PENDING = "issues:list_pending"
    RECOMMENDATIONS_READ = "recommendations:read"
    RECOMMENDATIONS_WRITE = "recommendations:write"
    PLANNING_READ = "planning:read"
    PLANNING_WRITE = "planning:write"
    SPATIAL_READ = "spatial:read"
    COPILOT_QUERY = "copilot:query"
    PROACTIVE_READ = "proactive:read"
    PIPELINE_READ = "pipeline:read"
    BRIEF_READ = "brief:read"
    TIMELINE_READ = "timeline:read"
    CONSTITUENCY_READ = "constituency:read"
    INCIDENTS_READ = "incidents:read"
    INCIDENTS_WRITE = "incidents:write"
    AUDIT_READ = "audit:read"
    AUDIT_WRITE = "audit:write"
    SYSTEM_ADMIN = "system:admin"


ROLE_PERMISSIONS: dict[str, set[str]] = {
    "System Administrator": {
        Permissions.ISSUES_CREATE,
        Permissions.ISSUES_READ,
        Permissions.ISSUES_LIST_PENDING,
        Permissions.RECOMMENDATIONS_READ,
        Permissions.RECOMMENDATIONS_WRITE,
        Permissions.PLANNING_READ,
        Permissions.PLANNING_WRITE,
        Permissions.SPATIAL_READ,
        Permissions.COPILOT_QUERY,
        Permissions.PROACTIVE_READ,
        Permissions.PIPELINE_READ,
        Permissions.BRIEF_READ,
        Permissions.TIMELINE_READ,
        Permissions.CONSTITUENCY_READ,
        Permissions.INCIDENTS_READ,
        Permissions.INCIDENTS_WRITE,
        Permissions.AUDIT_READ,
        Permissions.AUDIT_WRITE,
        Permissions.SYSTEM_ADMIN,
    },
    "Platform Administrator": {
        Permissions.ISSUES_CREATE,
        Permissions.ISSUES_READ,
        Permissions.ISSUES_LIST_PENDING,
        Permissions.RECOMMENDATIONS_READ,
        Permissions.RECOMMENDATIONS_WRITE,
        Permissions.PLANNING_READ,
        Permissions.PLANNING_WRITE,
        Permissions.SPATIAL_READ,
        Permissions.COPILOT_QUERY,
        Permissions.PROACTIVE_READ,
        Permissions.PIPELINE_READ,
        Permissions.BRIEF_READ,
        Permissions.TIMELINE_READ,
        Permissions.CONSTITUENCY_READ,
        Permissions.INCIDENTS_READ,
        Permissions.INCIDENTS_WRITE,
        Permissions.AUDIT_READ,
        Permissions.SYSTEM_ADMIN,
    },
    "MLA": {
        Permissions.ISSUES_READ,
        Permissions.ISSUES_LIST_PENDING,
        Permissions.RECOMMENDATIONS_READ,
        Permissions.PLANNING_READ,
        Permissions.PLANNING_WRITE,
        Permissions.SPATIAL_READ,
        Permissions.COPILOT_QUERY,
        Permissions.PROACTIVE_READ,
        Permissions.PIPELINE_READ,
        Permissions.BRIEF_READ,
        Permissions.TIMELINE_READ,
        Permissions.CONSTITUENCY_READ,
    },
    "MP": {
        Permissions.ISSUES_READ,
        Permissions.ISSUES_LIST_PENDING,
        Permissions.RECOMMENDATIONS_READ,
        Permissions.PLANNING_READ,
        Permissions.SPATIAL_READ,
        Permissions.COPILOT_QUERY,
        Permissions.PROACTIVE_READ,
        Permissions.PIPELINE_READ,
        Permissions.BRIEF_READ,
        Permissions.TIMELINE_READ,
        Permissions.CONSTITUENCY_READ,
    },
    "Officer": {
        Permissions.ISSUES_CREATE,
        Permissions.ISSUES_READ,
        Permissions.ISSUES_LIST_PENDING,
        Permissions.RECOMMENDATIONS_READ,
        Permissions.RECOMMENDATIONS_WRITE,
        Permissions.PLANNING_READ,
        Permissions.PLANNING_WRITE,
        Permissions.SPATIAL_READ,
        Permissions.COPILOT_QUERY,
        Permissions.PROACTIVE_READ,
        Permissions.PIPELINE_READ,
        Permissions.BRIEF_READ,
        Permissions.TIMELINE_READ,
        Permissions.CONSTITUENCY_READ,
        Permissions.INCIDENTS_READ,
        Permissions.INCIDENTS_WRITE,
    },
    "Field Engineer": {
        Permissions.ISSUES_READ,
        Permissions.SPATIAL_READ,
        Permissions.TIMELINE_READ,
    },
    "Citizen": {
        Permissions.ISSUES_CREATE,
        Permissions.ISSUES_READ,
        Permissions.SPATIAL_READ,
        Permissions.TIMELINE_READ,
    },
}


class CurrentUser:
    def __init__(self, user_id: str | None, role: str, permissions: set[str]):
        self.user_id = user_id
        self.role = role
        self.permissions = permissions


def normalize_role(role_str: str | None) -> str | None:
    if not role_str:
        return None
    r = role_str.strip().lower().replace("_", " ")
    if r in ("system administrator", "administrator", "admin"):
        return "System Administrator"
    if r in ("platform administrator", "platform admin"):
        return "Platform Administrator"
    if r == "mla":
        return "MLA"
    if r == "mp":
        return "MP"
    if r == "officer":
        return "Officer"
    if r in ("field engineer", "field crew", "engineer"):
        return "Field Engineer"
    if r == "citizen":
        return "Citizen"
    return None


def get_user_permissions(role_name: str) -> set[str]:
    """Retrieves all permissions for a given role name, resolving inheritance dynamically."""
    from sqlalchemy import text

    from helix_platform.persistence import SessionLocal

    static_perms = ROLE_PERMISSIONS.get(role_name, set())

    db = SessionLocal()
    try:
        # Check if roles table exists and is seeded
        roles_exist = db.execute(text("SELECT COUNT(*) FROM roles")).scalar()
        if not roles_exist:
            return static_perms

        permissions = set()
        current_role_name = role_name
        visited_roles = set()

        while current_role_name and current_role_name not in visited_roles:
            visited_roles.add(current_role_name)
            role_row = db.execute(
                text("SELECT id, parent_role_id FROM roles WHERE name = :name"),
                {"name": current_role_name},
            ).first()
            if not role_row:
                if len(visited_roles) == 1:
                    # TODO: REMOVE STATIC ROLE_PERMISSIONS fallback before release
                    return static_perms
                break
            role_id, parent_role_id = role_row[0], role_row[1]

            # Query permissions for this role
            perm_rows = db.execute(
                text(
                    "SELECT p.name FROM permissions p "
                    "JOIN role_permissions rp ON p.id = rp.permission_id "
                    "WHERE rp.role_id = :role_id"
                ),
                {"role_id": role_id},
            ).fetchall()

            for row in perm_rows:
                permissions.add(row[0])

            if not parent_role_id:
                break

            parent_role_row = db.execute(
                text("SELECT name FROM roles WHERE id = :id"), {"id": parent_role_id}
            ).first()
            current_role_name = parent_role_row[0] if parent_role_row else None

        return permissions
    except Exception:
        return static_perms
    finally:
        db.close()


def get_current_user_from_request(request: Request) -> CurrentUser:
    role_str = None
    user_id = None

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = decode_access_token(token)
            role_str = payload.get("role")
            user_id = payload.get("sub") or payload.get("user_id")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
            ) from e

    if not role_str:
        role_str = request.headers.get("X-User-Role")

    if not role_str:
        role_str = request.query_params.get("role")

    if not role_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials missing or invalid",
        )

    normalized_role = normalize_role(role_str)
    if not normalized_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid role: {role_str}",
        )

    permissions = get_user_permissions(normalized_role)
    return CurrentUser(user_id=user_id, role=normalized_role, permissions=permissions)


def get_current_user(
    request: Request,
    token: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> CurrentUser:
    if token:
        try:
            payload = decode_access_token(token.credentials)
            role_str = payload.get("role")
            user_id = payload.get("sub") or payload.get("user_id")
            normalized_role = normalize_role(role_str)
            if not normalized_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Invalid role: {role_str}",
                )
            permissions = get_user_permissions(normalized_role)
            return CurrentUser(
                user_id=user_id, role=normalized_role, permissions=permissions
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
            ) from e

    return get_current_user_from_request(request)


def require_permission(permission: str) -> Callable[[CurrentUser], CurrentUser]:
    def check_perm(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if permission not in user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: required permission '{permission}' not found for role '{user.role}'",
            )
        return user

    return check_perm


def has_permission(
    permission: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                request = kwargs.get("request")
                if not request:
                    for arg in args:
                        if isinstance(arg, Request):
                            request = arg
                            break
                if not request:
                    raise RuntimeError(
                        "Request object must be in route signature to use @has_permission decorator"
                    )

                user = get_current_user_from_request(request)
                if permission not in user.permissions:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission denied: required permission '{permission}' not found for role '{user.role}'",
                    )
                if "current_user" in kwargs:
                    kwargs["current_user"] = user
                return await func(*args, **kwargs)

            return async_wrapper

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            request = kwargs.get("request")
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            if not request:
                raise RuntimeError(
                    "Request object must be in route signature to use @has_permission decorator"
                )

            user = get_current_user_from_request(request)
            if permission not in user.permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: required permission '{permission}' not found for role '{user.role}'",
                )
            if "current_user" in kwargs:
                kwargs["current_user"] = user
            return func(*args, **kwargs)

        return sync_wrapper

    return decorator
