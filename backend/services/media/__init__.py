from fastapi import APIRouter

router = APIRouter(prefix="/media", tags=["Media"])


@router.get("")
@router.get("/")
def get_root() -> dict[str, str]:
    """Media Service status endpoint."""
    return {"service": "Media Service", "status": "active"}
