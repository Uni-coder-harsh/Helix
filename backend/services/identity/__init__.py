from fastapi import APIRouter

router = APIRouter(prefix="/identity", tags=["Identity"])


@router.get("")
@router.get("/")
def get_root() -> dict[str, str]:
    """Identity Service status endpoint."""
    return {"service": "Identity Service", "status": "active"}
