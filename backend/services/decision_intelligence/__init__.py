from fastapi import APIRouter

router = APIRouter(prefix="/decision-intelligence", tags=["Decision Intelligence"])


@router.get("")
@router.get("/")
def get_root() -> dict[str, str]:
    """Decision Intelligence Service status endpoint."""
    return {"service": "Decision Intelligence Service", "status": "active"}
