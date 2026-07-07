from fastapi import APIRouter, Depends

from helix_platform.security import CurrentUser, Permissions, require_permission

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("")
@router.get("/")
def get_root(
    _current_user: CurrentUser = Depends(require_permission(Permissions.AUDIT_READ)),
) -> dict[str, str]:
    """Audit Service status endpoint."""
    return {"service": "Audit Service", "status": "active"}
