from fastapi import APIRouter

router = APIRouter(prefix="/plugin", tags=["Plugin"])


@router.get("")
@router.get("/")
def get_root() -> dict[str, str]:
    """Plugin Service status endpoint."""
    return {"service": "Plugin Service", "status": "active"}
