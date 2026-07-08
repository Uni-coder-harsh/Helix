# Expose routers and models for identity service
from services.identity.models import UserDB
from services.identity.routes import router

__all__ = ["UserDB", "router"]
