from fastapi import APIRouter, Depends

from helix_platform.security import CurrentUser, Permissions, require_permission

router = APIRouter(prefix="/media", tags=["Media"])


@router.get("")
@router.get("/")
def get_root(
    _current_user: CurrentUser = Depends(require_permission(Permissions.ISSUES_READ)),
) -> dict[str, str]:
    """Media Service status endpoint."""
    return {"service": "Media Service", "status": "active"}
