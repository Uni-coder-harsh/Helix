from fastapi import APIRouter, Depends

from helix_platform.security import CurrentUser, Permissions, require_permission

router = APIRouter(prefix="/plugin", tags=["Plugin"])


@router.get("")
@router.get("/")
def get_root(
    _current_user: CurrentUser = Depends(require_permission(Permissions.SYSTEM_ADMIN)),
) -> dict[str, str]:
    """Plugin Service status endpoint."""
    return {"service": "Plugin Service", "status": "active"}
