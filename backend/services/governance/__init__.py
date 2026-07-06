import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from helix_platform.persistence import get_db
from helix_platform.spatial import GeoService, IssueClustering
from services.governance.application.copilot import GovernanceCopilotService
from services.governance.application.proactive import ProactiveIntelligenceService
from services.governance.application.queries import GovernanceQueryService

# Application & Domain Layers
from services.governance.application.services import (
    IssueApplicationService,
    OfficerApplicationService,
    RecommendationApplicationService,
)
from services.governance.infrastructure.queries import SQLAlchemyGovernanceQueryService

# Infrastructure Layer
from services.governance.infrastructure.repositories import (
    LogNotificationRepository,
    SQLAlchemyIssueRepository,
    SQLAlchemyRecommendationRepository,
)
from services.governance.workflows import knowledge_service

router = APIRouter(prefix="/governance", tags=["Governance"])


# Pydantic schemas for request validation
class IssueCreateSchema(BaseModel):
    citizen_id: str = Field(..., description="UUID of the submitting citizen")
    title: str = Field(
        ..., min_length=3, max_length=255, description="Brief title of the issue"
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=2048,
        description="Detailed explanation of the issue",
    )
    category: str = Field(..., description="E.g., sanitation, roads, general")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    formatted_address: str = Field(
        ..., description="Formatted textual address of the issue location"
    )


class RecommendationVerdictSchema(BaseModel):
    reason: str = Field(
        default="No reason provided", description="Reason for rejection"
    )


# Dependency Injection Helpers
def get_issue_repo(db: Session = Depends(get_db)) -> SQLAlchemyIssueRepository:
    return SQLAlchemyIssueRepository(db)


def get_rec_repo(
    db: Session = Depends(get_db),
) -> SQLAlchemyRecommendationRepository:
    return SQLAlchemyRecommendationRepository(db)


def get_notification_repo() -> LogNotificationRepository:
    return LogNotificationRepository()


def get_query_service(
    db: Session = Depends(get_db),
) -> SQLAlchemyGovernanceQueryService:
    return SQLAlchemyGovernanceQueryService(db)


def get_issue_service(
    repo: SQLAlchemyIssueRepository = Depends(get_issue_repo),
) -> IssueApplicationService:
    return IssueApplicationService(repo)


def get_rec_service(
    repo: SQLAlchemyRecommendationRepository = Depends(get_rec_repo),
) -> RecommendationApplicationService:
    return RecommendationApplicationService(repo)


def get_officer_service(
    issue_repo: SQLAlchemyIssueRepository = Depends(get_issue_repo),
    rec_repo: SQLAlchemyRecommendationRepository = Depends(get_rec_repo),
    notification_repo: LogNotificationRepository = Depends(get_notification_repo),
) -> OfficerApplicationService:
    return OfficerApplicationService(issue_repo, rec_repo, notification_repo)


@router.get("")
@router.get("/")
async def get_root() -> dict[str, str]:
    """Governance Service status endpoint."""
    return {"service": "Governance Service", "status": "active"}


@router.post("/issues", response_model=dict[str, Any])
async def submit_issue(
    payload: IssueCreateSchema,
    issue_service: IssueApplicationService = Depends(get_issue_service),
) -> dict[str, Any]:
    """1. Citizen submits an issue, triggering the ingestion pipeline."""
    issue_id = await issue_service.ingest_issue(
        citizen_id=uuid.UUID(payload.citizen_id),
        title=payload.title,
        description=payload.description,
        category=payload.category,
        latitude=payload.latitude,
        longitude=payload.longitude,
        formatted_address=payload.formatted_address,
    )
    return {"issue_id": issue_id, "status": "INTAKE"}


@router.get("/issues/pending", response_model=list[dict[str, Any]])
async def list_pending_issues(
    query_service: GovernanceQueryService = Depends(get_query_service),
) -> list[dict[str, Any]]:
    """List pending issues waiting for triage or AI recommendation review."""
    return query_service.list_pending_issues()


@router.get("/recommendations/{issue_id}", response_model=dict[str, Any])
async def get_recommendation(
    issue_id: str,
    query_service: GovernanceQueryService = Depends(get_query_service),
) -> dict[str, Any]:
    """Retrieve the AI recommendation for a specific issue."""
    try:
        return query_service.get_recommendation_details(uuid.UUID(issue_id))
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post(
    "/recommendations/{recommendation_id}/accept", response_model=dict[str, Any]
)
async def accept_recommendation(
    recommendation_id: str,
    officer_service: OfficerApplicationService = Depends(get_officer_service),
) -> dict[str, Any]:
    """Approve the AI recommendation, assigning the task and transitioning state."""
    try:
        decision_id = await officer_service.accept_recommendation(
            uuid.UUID(recommendation_id)
        )
        return {
            "status": "SUCCESS",
            "decision_id": decision_id,
            "new_issue_status": "ASSIGNED",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post(
    "/recommendations/{recommendation_id}/reject", response_model=dict[str, Any]
)
async def reject_recommendation(
    recommendation_id: str,
    payload: RecommendationVerdictSchema,
    officer_service: OfficerApplicationService = Depends(get_officer_service),
) -> dict[str, Any]:
    """Reject the AI recommendation."""
    try:
        await officer_service.reject_recommendation(
            uuid.UUID(recommendation_id), payload.reason
        )
        return {"status": "SUCCESS", "new_issue_status": "REJECTED"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/dashboard/stats", response_model=dict[str, int])
async def get_dashboard_stats(
    query_service: GovernanceQueryService = Depends(get_query_service),
) -> dict[str, int]:
    """Compute summary statistics for issues grouped by status mapping."""
    return query_service.get_dashboard_stats()


@router.get("/issues/{issue_id}/context", response_model=dict[str, Any])
async def get_issue_context(
    issue_id: str,
    query_service: GovernanceQueryService = Depends(get_query_service),
) -> dict[str, Any]:
    """Retrieve the full decision context (policies, schemes, assets, impact, alternatives) for an issue."""
    issues = query_service.list_pending_issues()
    issue = next((i for i in issues if str(i["id"]) == issue_id), None)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    from services.governance.workflows import rec_builder

    rec_details = rec_builder.build_recommendation(
        issue_id=uuid.UUID(issue_id),
        category=issue["category"],
        latitude=issue["latitude"],
        longitude=issue["longitude"],
    )
    rec_details["priority"] = str(rec_details["priority"].name)
    return rec_details


# Spatial Engine Integration Endpoints


def get_geo_service() -> GeoService:
    return GeoService()


@router.get("/spatial/boundaries", response_model=dict[str, Any])
async def get_spatial_boundaries(
    geo_service: GeoService = Depends(get_geo_service),
) -> dict[str, Any]:
    """Retrieve GeoJSON features representing constituency and ward boundaries."""
    return geo_service.get_boundaries_as_geojson()


@router.get("/spatial/heatmap", response_model=list[dict[str, Any]])
async def get_spatial_heatmap(
    query_service: GovernanceQueryService = Depends(get_query_service),
    geo_service: GeoService = Depends(get_geo_service),
) -> list[dict[str, Any]]:
    """Retrieve weighted heatmap coordinates of all lodged complaints."""
    issues = query_service.list_pending_issues()
    return geo_service.generate_heatmap_data(issues)


@router.get("/spatial/clusters", response_model=list[dict[str, Any]])
async def get_spatial_clusters(
    query_service: GovernanceQueryService = Depends(get_query_service),
) -> list[dict[str, Any]]:
    """Retrieve clustered issue markers for map visualization."""
    issues = query_service.list_pending_issues()
    return IssueClustering.cluster_issues(issues, radius_km=0.5)


# Governance Copilot API Endpoints


class CopilotRequestSchema(BaseModel):
    action: str = Field(description="Action name (e.g. decision_summary)")
    issue_id: str | None = Field(default=None, description="Target issue context")
    query_details: dict[str, Any] = Field(
        default_factory=dict, description="Query context"
    )


def get_copilot_service(
    query_service: GovernanceQueryService = Depends(get_query_service),
) -> GovernanceCopilotService:
    return GovernanceCopilotService(
        knowledge_service=knowledge_service,
        query_service=query_service,
    )


@router.post("/copilot", response_model=dict[str, Any])
async def execute_copilot_query(
    payload: CopilotRequestSchema,
    copilot_service: GovernanceCopilotService = Depends(get_copilot_service),
) -> dict[str, Any]:
    """Execute a structured decision query against the Governance Copilot."""
    try:
        return await copilot_service.execute_query(
            action=payload.action,
            issue_id=payload.issue_id,
            query_details=payload.query_details,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


def get_proactive_service(
    query_service: GovernanceQueryService = Depends(get_query_service),
) -> ProactiveIntelligenceService:
    return ProactiveIntelligenceService(query_service=query_service)


@router.get("/proactive/morning-brief", response_model=dict[str, Any])
async def get_morning_briefing(
    proactive_service: ProactiveIntelligenceService = Depends(get_proactive_service),
) -> dict[str, Any]:
    """Retrieve proactive MLA morning briefings, risk alerts, and forecast trends."""
    return proactive_service.get_morning_briefing()
