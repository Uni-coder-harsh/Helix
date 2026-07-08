from fastapi import APIRouter, Depends

from helix_platform.security import CurrentUser, Permissions, require_permission

router = APIRouter(prefix="/ai-platform", tags=["AI Platform"])


@router.get("")
@router.get("/")
def get_root(
    _current_user: CurrentUser = Depends(
        require_permission(Permissions.RECOMMENDATIONS_READ)
    ),
) -> dict[str, str]:
    """AI Platform Service status endpoint."""
    return {"service": "AI Platform Service", "status": "active"}
