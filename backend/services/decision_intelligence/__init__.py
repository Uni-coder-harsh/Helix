from fastapi import APIRouter, Depends

from helix_platform.security import CurrentUser, Permissions, require_permission

router = APIRouter(prefix="/decision-intelligence", tags=["Decision Intelligence"])


@router.get("")
@router.get("/")
def get_root(
    _current_user: CurrentUser = Depends(
        require_permission(Permissions.CONSTITUENCY_READ)
    ),
) -> dict[str, str]:
    """Decision Intelligence Service status endpoint."""
    return {"service": "Decision Intelligence Service", "status": "active"}
