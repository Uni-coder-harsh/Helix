from fastapi import APIRouter

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("")
@router.get("/")
def get_root() -> dict[str, str]:
    """Audit Service status endpoint."""
    return {"service": "Audit Service", "status": "active"}
