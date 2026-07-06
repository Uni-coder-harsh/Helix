from fastapi import APIRouter

router = APIRouter(prefix="/ai-platform", tags=["AI Platform"])


@router.get("")
@router.get("/")
def get_root() -> dict[str, str]:
    """AI Platform Service status endpoint."""
    return {"service": "AI Platform Service", "status": "active"}
