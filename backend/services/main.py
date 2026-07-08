import sys
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

sys.path.append(str(Path(__file__).resolve().parent.parent))
import services.ai_platform as ai_platform
import services.audit as audit
import services.decision_intelligence as decision_intelligence
import services.governance as governance
import services.identity as identity
import services.media as media
import services.plugin as plugin
from helix_platform.config import get_settings
from helix_platform.logging import (
    configure_logging,
    correlation_id_var,
    get_logger,
    request_id_var,
)
from helix_platform.persistence import engine
from helix_platform.runtime import configure_asyncio_runtime
from helix_platform.telemetry import instrument_app, setup_telemetry

# Ensure asyncio wakeups remain functional in restricted runtimes.
configure_asyncio_runtime()

# 1. Initialize logging
configure_logging()
logger = get_logger("bootstrap")

# 2. Load configurations
settings = get_settings()

# 3. Setup OpenTelemetry
setup_telemetry(settings.APP_NAME)

# 4. Initialize database and register subscriptions at startup
from services.governance.workflows import register_subscriptions

register_subscriptions()

import services.governance.infrastructure.models
import services.identity.models
from helix_platform.persistence import Base, SessionLocal
from services.identity.seed import seed_database

Base.metadata.create_all(bind=engine)

# Seed database with standard lookup tables and default System Admin
db = SessionLocal()
try:
    if not db.query(services.identity.models.UserDB).first():
        seed_database(db)
finally:
    db.close()


# 5. Create FastAPI instance
app = FastAPI(
    title="Helix Governance OS Core API",
    description="Modular monolith containing all 7 Helix core services.",
    version=settings.APP_VERSION,
)

# 5. OpenTelemetry Instrumentation
instrument_app(app)


# 6. Structured Logging & Context Correlation Middleware
class LoggingAndCorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        # Extract or generate Correlation & Request IDs
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        correlation_id = request.headers.get("X-Correlation-ID", request_id)

        # Bind context variables for log processors
        request_id_var.set(request_id)
        correlation_id_var.set(correlation_id)

        start_time = time.perf_counter()

        logger.info(
            "http_request_received",
            method=request.method,
            path=request.url.path,
            client_host=request.client.host if request.client else None,
        )

        try:
            response: Response = await call_next(request)
            duration = time.perf_counter() - start_time

            # Propagate tracking IDs in response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = correlation_id

            logger.info(
                "http_request_processed",
                status_code=response.status_code,
                duration_seconds=round(duration, 4),
            )
            return response
        except Exception as e:
            duration = time.perf_counter() - start_time
            logger.error(
                "http_request_failed",
                error=str(e),
                duration_seconds=round(duration, 4),
                exc_info=True,
            )
            raise e


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingAndCorrelationMiddleware)

# 7. Mount Service Routers (Scaffolding the Modular Monolith)
app.include_router(governance.router)
app.include_router(identity.router)
app.include_router(ai_platform.router)
app.include_router(media.router)
app.include_router(audit.router)
app.include_router(plugin.router)
app.include_router(decision_intelligence.router)


# 8. Health & Version Endpoints
@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Overall status health check."""
    return {"status": "healthy", "service": settings.APP_NAME}


@app.get("/health/liveness", tags=["Health"])
def liveness_check() -> dict[str, str]:
    """Liveness probe to check process execution."""
    return {"status": "alive"}


@app.get("/live", tags=["Health"])
def live_check() -> dict[str, str]:
    """Alias for liveness check."""
    return liveness_check()


@app.get("/health/readiness", tags=["Health"])
def readiness_check() -> dict[str, Any]:
    """Readiness probe to check backend service and database health."""
    db_status = "healthy"
    try:
        # Verify db engine connectivity
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
    except Exception as e:
        logger.error("readiness_db_connection_failed", error=str(e))
        db_status = "unhealthy"

    status_code = "ready" if db_status == "healthy" else "not_ready"
    return {
        "status": status_code,
        "dependencies": {
            "database": db_status,
        },
    }


@app.get("/ready", tags=["Health"])
def ready_check() -> dict[str, Any]:
    """Alias for readiness check."""
    return readiness_check()


@app.get("/version", tags=["Health"])
def version_info() -> dict[str, str]:
    """Version check metadata endpoint."""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENV,
    }
