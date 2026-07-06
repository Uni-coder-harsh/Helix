from fastapi import APIRouter

router = APIRouter(prefix="/governance", tags=["Governance"])


@router.get("")
@router.get("/")
def get_root() -> dict[str, str]:
    """Governance Service status endpoint."""
    return {"service": "Governance Service", "status": "active"}
