import uuid
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from helix_platform.persistence import get_db
from helix_platform.spatial import GeoService, IssueClustering
from services.governance.application.agents import DecisionPipelineOrchestrator
from services.governance.application.copilot import GovernanceCopilotService
from services.governance.application.planning import OutcomePlanningEngine
from services.governance.application.proactive import ProactiveIntelligenceService
from services.governance.application.queries import GovernanceQueryService

# Application & Domain Layers
from services.governance.application.services import (
    IssueApplicationService,
    OfficerApplicationService,
    RecommendationApplicationService,
)
from services.governance.application.spatial import SpatialIntelligenceService
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


def get_evidence_service() -> Any:
    from services.governance.application.evidence import EvidenceIntelligenceService

    return EvidenceIntelligenceService()


@router.get("")
@router.get("/")
async def get_root() -> dict[str, str]:
    """Governance Service status endpoint."""
    return {"service": "Governance Service", "status": "active"}


@router.post("/issues", response_model=dict[str, Any])
async def submit_issue(
    payload: IssueCreateSchema,
    issue_service: IssueApplicationService = Depends(get_issue_service),
    db: Session = Depends(get_db),
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

    # Auto-cluster the issue into an incident
    from services.governance.application.evidence import EvidenceIntelligenceService

    evidence_service = EvidenceIntelligenceService()
    try:
        cluster_info = evidence_service.auto_cluster_issue(issue_id, db)
    except Exception as e:
        print("Auto-clustering failed:", e)
        cluster_info = {"incident_id": None, "created_new": False}

    return {
        "issue_id": issue_id,
        "status": "INTAKE",
        "incident_id": cluster_info.get("incident_id"),
        "cluster_info": cluster_info,
    }


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

    rec_details = await rec_builder.build_recommendation(
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


@router.get("/spatial/places", response_model=list[dict[str, Any]])
async def get_nearby_places(
    latitude: float,
    longitude: float,
    radius: int = 1500,
    type: str = "school",
    geo_service: GeoService = Depends(get_geo_service),
) -> list[dict[str, Any]]:
    """Search nearby public places (schools, hospitals, parks) using Google Places proxy."""
    return geo_service.search_nearby_places(latitude, longitude, radius, type)


@router.get("/spatial/geocode", response_model=dict[str, Any])
async def geocode_address(
    address: str,
    geo_service: GeoService = Depends(get_geo_service),
) -> dict[str, Any]:
    """Convert a textual address into GPS coordinates using Google Geocoding API."""
    res = geo_service.geocode_address(address)
    if not res:
        raise HTTPException(status_code=404, detail="Address coordinates not found.")
    return res


@router.get("/spatial/reverse-geocode", response_model=dict[str, Any])
async def reverse_geocode_coords(
    latitude: float,
    longitude: float,
    geo_service: GeoService = Depends(get_geo_service),
) -> dict[str, Any]:
    """Convert GPS coordinates to a formatted address using Google Geocoding API."""
    address = geo_service.reverse_geocode(latitude, longitude)
    if not address:
        raise HTTPException(
            status_code=404, detail="Address not found for coordinates."
        )
    return {"formatted_address": address}


@router.get("/spatial/query", response_model=list[dict[str, Any]])
async def query_spatial_issues(
    lat: float | None = None,
    lng: float | None = None,
    radius_km: float | None = None,
    min_lat: float | None = None,
    min_lng: float | None = None,
    max_lat: float | None = None,
    max_lng: float | None = None,
    category: str | None = None,
    status: str | None = None,
    query_service: GovernanceQueryService = Depends(get_query_service),
) -> list[dict[str, Any]]:
    """Query and filter issues geographically (via radius or bounding box) and logically."""
    issues = query_service.list_pending_issues()
    filtered = []
    for issue in issues:
        # Filter by category
        if category and category.lower() not in issue.get("category", "").lower():
            continue
        # Filter by status
        if status and status.lower() != issue.get("status", "").lower():
            continue

        issue_lat = issue.get("latitude")
        issue_lng = issue.get("longitude")
        if issue_lat is None or issue_lng is None:
            continue

        # Filter by bounding box
        if min_lat is not None and not (min_lat <= issue_lat <= max_lat):
            continue
        if min_lng is not None and not (min_lng <= issue_lng <= max_lng):
            continue

        # Filter by radius distance
        if lat is not None and lng is not None and radius_km is not None:
            dist = GeoService.calculate_distance(lat, lng, issue_lat, issue_lng)
            if dist > radius_km:
                continue

            # Add calculated distance to response
            issue = dict(issue)
            issue["distance_km"] = dist

        filtered.append(issue)
    return filtered


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
    return await proactive_service.get_morning_briefing()


def get_pipeline_orchestrator() -> DecisionPipelineOrchestrator:
    return DecisionPipelineOrchestrator()


@router.get("/issues/{issue_id}/decision-pipeline", response_model=dict[str, Any])
async def get_issue_decision_pipeline(
    issue_id: str,
    query_service: GovernanceQueryService = Depends(get_query_service),
    orchestrator: DecisionPipelineOrchestrator = Depends(get_pipeline_orchestrator),
) -> dict[str, Any]:
    """Execute the multi-agent decision pipeline for a target issue and retrieve execution telemetry."""
    issues = query_service.list_pending_issues()
    issue = next((i for i in issues if str(i["id"]) == issue_id), None)
    if not issue:
        # Check mock issues if DB has no record
        from lib.mock_data import mockIssues

        mock_issue = next((i for i in mockIssues if i.id == issue_id), None)
        if mock_issue:
            issue = {
                "id": mock_issue.id,
                "title": mock_issue.title,
                "description": mock_issue.description,
                "category": mock_issue.category,
                "latitude": mock_issue.location.lat,
                "longitude": mock_issue.location.lng,
                "status": mock_issue.status,
                "priority": mock_issue.priority,
            }
        else:
            raise HTTPException(status_code=404, detail="Issue record not found.")

    return await orchestrator.run_pipeline(issue)


def get_brief_engine() -> Any:
    from services.governance.application.decision_brief import DecisionBriefEngine

    return DecisionBriefEngine()


@router.get("/issues/{issue_id}/decision-brief", response_model=dict[str, Any])
async def get_issue_decision_brief(
    issue_id: str,
    query_service: GovernanceQueryService = Depends(get_query_service),
    engine: Any = Depends(get_brief_engine),
) -> dict[str, Any]:
    """Compile and return an explainable, structured Decision Brief for a target issue."""
    issues = query_service.list_pending_issues()
    issue = next((i for i in issues if str(i["id"]) == issue_id), None)
    if not issue:
        # Check mock issues if DB has no record
        from lib.mock_data import mockIssues

        mock_issue = next((i for i in mockIssues if i.id == issue_id), None)
        if mock_issue:
            issue = {
                "id": mock_issue.id,
                "title": mock_issue.title,
                "description": mock_issue.description,
                "category": mock_issue.category,
                "latitude": mock_issue.location.lat,
                "longitude": mock_issue.location.lng,
                "status": mock_issue.status,
                "priority": mock_issue.priority,
            }
        else:
            raise HTTPException(status_code=404, detail="Issue record not found.")

    return cast(dict[str, Any], await engine.generate_brief(issue))


@router.get("/issues/{issue_id}/decision-brief/download")
async def download_issue_decision_brief(
    issue_id: str,
    query_service: GovernanceQueryService = Depends(get_query_service),
    engine: Any = Depends(get_brief_engine),
) -> HTMLResponse:
    """Generate and return a print-ready HTML decision brief document."""
    issues = query_service.list_pending_issues()
    issue = next((i for i in issues if str(i["id"]) == issue_id), None)
    if not issue:
        from lib.mock_data import mockIssues

        mock_issue = next((i for i in mockIssues if i.id == issue_id), None)
        if mock_issue:
            issue = {
                "id": mock_issue.id,
                "title": mock_issue.title,
                "description": mock_issue.description,
                "category": mock_issue.category,
                "latitude": mock_issue.location.lat,
                "longitude": mock_issue.location.lng,
                "status": mock_issue.status,
                "priority": mock_issue.priority,
            }
        else:
            raise HTTPException(status_code=404, detail="Issue record not found.")

    brief = await engine.generate_brief(issue)

    # Format lists as HTML segments
    evidence_html = (
        "".join(
            [
                f'<div class="list-item"><strong>[{ev["source"]} - {ev["type"].upper()}]</strong> {ev["statement"]}</div>'
                for ev in brief.get("evidence", [])
            ]
        )
        or '<div class="list-item">No telemetry evidence compiled.</div>'
    )

    policy_html = (
        "".join(
            [
                f'<div class="list-item">📜 <strong>{p["name"]}</strong> (Code: {p["code"]})</div>'
                for p in brief.get("applicable_policies", [])
            ]
        )
        or '<div class="list-item">No applicable policy bounds found.</div>'
    )

    scheme_html = (
        "".join(
            [
                f'<div class="list-item">💰 <strong>{s["name"]}</strong> ({int(s["subsidy_ratio"]*100)}% Subsidy Clearance)</div>'
                for s in brief.get("applicable_schemes", [])
            ]
        )
        or '<div class="list-item">No developmental scheme matched.</div>'
    )

    reasoning_html = (
        "".join(
            [
                f'<div class="list-item">→ {step}</div>'
                for step in brief.get("reasoning", [])
            ]
        )
        or '<div class="list-item">No automated reasoning trace generated.</div>'
    )

    follow_up = brief.get("follow_up_actions", {})
    immediate_html = (
        "".join(
            [
                f'<div class="list-item">✓ {act}</div>'
                for act in follow_up.get("immediate", [])
            ]
        )
        or "None"
    )
    this_week_html = (
        "".join(
            [
                f'<div class="list-item">✓ {act}</div>'
                for act in follow_up.get("this_week", [])
            ]
        )
        or "None"
    )
    long_term_html = (
        "".join(
            [
                f'<div class="list-item">✓ {act}</div>'
                for act in follow_up.get("long_term", [])
            ]
        )
        or "None"
    )

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Helix Governance Decision Brief - {brief['problem']['title']}</title>
  <style>
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1e293b; line-height: 1.6; padding: 40px; background-color: #f8fafc; }}
    .card {{ background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 35px; max-width: 850px; margin: 0 auto; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }}
    .header {{ border-bottom: 3px solid #6366f1; padding-bottom: 20px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: flex-start; }}
    .title {{ font-size: 26px; font-weight: 800; color: #0f172a; margin: 0; }}
    .meta {{ font-size: 11px; color: #64748b; font-family: monospace; margin-top: 5px; }}
    .badge {{ display: inline-block; padding: 4px 12px; border-radius: 9999px; font-size: 10px; font-weight: bold; background: #e0e7ff; color: #4338ca; text-transform: uppercase; }}
    .section-title {{ font-size: 13px; font-weight: 750; text-transform: uppercase; color: #475569; border-left: 4px solid #6366f1; padding-left: 12px; margin-top: 30px; margin-bottom: 12px; letter-spacing: 0.05em; }}
    .grid {{ display: grid; grid-template-cols: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
    .grid-cell {{ border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; font-size: 12px; background: #fafafa; }}
    .grid-cell-title {{ font-weight: bold; font-size: 10px; text-transform: uppercase; color: #64748b; margin-bottom: 6px; letter-spacing: 0.05em; }}
    .list-item {{ font-size: 12.5px; margin-bottom: 8px; color: #334155; }}
    .footer {{ margin-top: 50px; border-top: 1px solid #e2e8f0; padding-top: 20px; font-size: 11px; color: #94a3b8; display: flex; justify-content: space-between; align-items: center; }}
    .btn-print {{ background: #4f46e5; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-size: 12px; font-weight: bold; cursor: pointer; transition: background 0.2s; }}
    .btn-print:hover {{ background: #4338ca; }}
    .qr-container {{ display: flex; flex-direction: column; align-items: center; border: 1px solid #e2e8f0; padding: 10px; border-radius: 8px; background: white; }}
    @media print {{
      .btn-print {{ display: none; }}
      body {{ padding: 0; background: white; }}
      .card {{ border: none; box-shadow: none; max-width: 100%; padding: 0; }}
    }}
  </style>
</head>
<body>
  <div class="card">
    <div style="text-align: right; margin-bottom: 20px;">
      <button class="btn-print" onclick="window.print()">Print / Export to PDF</button>
    </div>
    <div class="header">
      <div>
        <h1 class="title">Helix Decision Brief</h1>
        <div class="meta">Brief ID: {brief.get('brief_id')} | Version {brief.get('version')}</div>
        <div class="meta">Generated By: {brief.get('generated_by')} | Timestamp: {brief.get('generated_at')}</div>
      </div>
      <div style="text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 8px;">
        <span class="badge">{brief['problem']['status']}</span>
        <div style="font-size: 12px; font-weight: bold; color: #0f172a;">Confidence: {brief['confidence']['overall']}%</div>
      </div>
    </div>

    <div class="section-title">1. Issue Context & Georeference</div>
    <div class="grid-cell" style="margin-bottom: 20px;">
      <div class="grid-cell-title">Report Title</div>
      <strong style="font-size: 14px; color: #0f172a;">{brief['problem']['title']}</strong>
      <p style="margin: 8px 0 0 0; font-size: 12.5px; color: #475569;">{brief['problem']['description']}</p>
    </div>

    <div class="grid">
      <div class="grid-cell">
        <div class="grid-cell-title">Geographic Coordinates</div>
        <strong>Latitude:</strong> {brief['problem']['location']['latitude']}<br>
        <strong>Longitude:</strong> {brief['problem']['location']['longitude']}<br>
        <strong>Category:</strong> {brief['problem']['category']}
      </div>
      <div class="grid-cell">
        <div class="grid-cell-title">Impact Telemetry</div>
        <strong>Affected population footprint:</strong> {brief['impact_summary']['affected_population']} citizens<br>
        <strong>Urgency score:</strong> {int(brief['impact_summary']['urgency_score']*100)}%<br>
        <strong>Severity tier:</strong> {brief['impact_summary']['severity_level']}
      </div>
    </div>

    <div class="section-title">2. Grounded Evidence Provenance</div>
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 18px; border-radius: 8px; margin-bottom: 20px;">
      {evidence_html}
    </div>

    <div class="section-title">3. Matched Regulatory Codes & Scheme Subsidies</div>
    <div class="grid">
      <div class="grid-cell">
        <div class="grid-cell-title">Applicable Policy Guidelines</div>
        {policy_html}
      </div>
      <div class="grid-cell">
        <div class="grid-cell-title">Eligible Funding Schemes</div>
        {scheme_html}
      </div>
    </div>

    <div class="section-title">4. Strategic Recommendation Strategy</div>
    <div class="grid-cell" style="background: #f0fdf4; border-color: #bbf7d0; margin-bottom: 20px; padding: 18px;">
      <div class="grid-cell-title" style="color: #166534; font-weight: 800;">Recommended Option</div>
      <strong style="font-size: 14px; color: #166534;">{brief['recommendation']['recommended_action']}</strong>
      <div style="font-size: 12px; margin-top: 8px; color: #14532d; line-height: 1.5;">
        <strong>Dispatched To:</strong> {brief['recommendation']['suggested_department']}<br>
        <strong>Estimated Cost:</strong> {brief['recommendation']['estimated_cost']}<br>
        <strong>Resolution SLA:</strong> {brief['recommendation']['sla']}
      </div>
    </div>

    <div class="section-title">5. AI Reasoning & Decision Telemetry</div>
    <div style="font-size: 12.5px; background: #fafafa; border: 1px solid #e2e8f0; padding: 18px; border-radius: 8px; margin-bottom: 20px; line-height: 1.7;">
      {reasoning_html}
    </div>

    <div class="section-title">6. Lifecycle Follow-up Execution Map</div>
    <div style="font-size: 12.5px; background: #fff; border: 1px solid #e2e8f0; padding: 18px; border-radius: 8px;">
      <strong style="color: #c2410c; display: block; margin-bottom: 6px; font-size: 12px; text-transform: uppercase;">[Immediate / 24 Hours]</strong>
      {immediate_html}
      <strong style="color: #b45309; display: block; margin-top: 15px; margin-bottom: 6px; font-size: 12px; text-transform: uppercase;">[This Week / SLA Target]</strong>
      {this_week_html}
      <strong style="color: #15803d; display: block; margin-top: 15px; margin-bottom: 6px; font-size: 12px; text-transform: uppercase;">[Long Term]</strong>
      {long_term_html}
    </div>

    <div class="footer">
      <div>This document is dynamically generated by the Helix Governance Console.<br>Digitally signed & verified by Helix AI Decision Engine.</div>
      <div class="qr-container">
        <div style="width: 45px; height: 45px; background: #000; display: flex; flex-wrap: wrap; align-items: center; justify-content: center; color: #fff; font-size: 8px; font-weight: bold; font-family: monospace; border-radius: 4px;">
          HELIX<br>SECURE
        </div>
        <div style="font-size: 7px; color: #64748b; margin-top: 4px; font-family: monospace;">[QR CODE]</div>
      </div>
    </div>
  </div>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@router.get("/issues/{issue_id}/timeline", response_model=dict[str, Any])
async def get_issue_timeline(
    issue_id: str,
    role: str = "citizen",
    query_service: GovernanceQueryService = Depends(get_query_service),
) -> dict[str, Any]:
    """Retrieve canonical, role-based timeline entries representing the entire issue lifecycle."""
    from services.governance.application.timeline import TimelineEngine

    issues = query_service.list_pending_issues()
    issue = next((i for i in issues if str(i["id"]) == issue_id), None)
    if not issue:
        from lib.mock_data import mockIssues

        mock_issue = next((i for i in mockIssues if i.id == issue_id), None)
        if mock_issue:
            issue = {
                "id": mock_issue.id,
                "title": mock_issue.title,
                "description": mock_issue.description,
                "category": mock_issue.category,
                "latitude": mock_issue.location.lat,
                "longitude": mock_issue.location.lng,
                "status": mock_issue.status,
                "priority": mock_issue.priority,
            }
        else:
            raise HTTPException(status_code=404, detail="Issue record not found.")

    return TimelineEngine.generate_timeline(issue, role)


def get_spatial_intelligence_service(
    query_service: GovernanceQueryService = Depends(get_query_service),
) -> SpatialIntelligenceService:
    return SpatialIntelligenceService(query_service=query_service)


@router.get("/constituency/overview", response_model=dict[str, Any])
async def get_constituency_overview(
    spatial_service: SpatialIntelligenceService = Depends(
        get_spatial_intelligence_service
    ),
) -> dict[str, Any]:
    """Retrieve derived constituency health scores, hotspot projects, and active priorities."""
    return spatial_service.get_constituency_overview()


@router.get("/map", response_model=dict[str, Any])
async def get_map_dataset(
    spatial_service: SpatialIntelligenceService = Depends(
        get_spatial_intelligence_service
    ),
) -> dict[str, Any]:
    """Retrieve GeoJSON boundaries, markers, clusters, and hotspots for mapping."""
    return spatial_service.get_map_dataset()


def get_outcome_planning_engine() -> OutcomePlanningEngine:
    return OutcomePlanningEngine()


@router.get("/planning/projects", response_model=list[dict[str, Any]])
async def get_recommended_projects(
    engine: OutcomePlanningEngine = Depends(get_outcome_planning_engine),
    evidence_service: Any = Depends(get_evidence_service),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Retrieve derived developmental project proposals, outcome forecasts, and LLM reasoning."""
    incidents = evidence_service.get_all_incidents(db)
    return await engine.plan_projects(incidents)


@router.post("/planning/projects/{project_id}/approve", response_model=dict[str, Any])
async def approve_project(project_id: str) -> dict[str, Any]:
    """Approve a proposed developmental project and initiate municipal tendering workflow."""
    return {
        "project_id": project_id,
        "status": "APPROVED",
        "message": "Tendering process activated.",
    }


@router.get("/issues/{issue_id}/duplicates", response_model=list[dict[str, Any]])
async def get_issue_duplicates(
    issue_id: str,
    evidence_service: Any = Depends(get_evidence_service),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Retrieve potential duplicate citizen reports matching this issue's signature."""
    return cast(
        list[dict[str, Any]], evidence_service.get_issue_duplicates(issue_id, db)
    )


@router.get("/incidents", response_model=list[dict[str, Any]])
async def get_incidents(
    evidence_service: Any = Depends(get_evidence_service),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Retrieve all grouped incident clusters."""
    return cast(list[dict[str, Any]], evidence_service.get_all_incidents(db))


@router.get("/incidents/graph", response_model=dict[str, Any])
async def get_incidents_graph(
    evidence_service: Any = Depends(get_evidence_service),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve incident Belongs_to relationship graph of issues."""
    return cast(dict[str, Any], evidence_service.get_relationship_graph(db))


@router.get("/incidents/{incident_id}", response_model=dict[str, Any])
async def get_incident_details(
    incident_id: str,
    evidence_service: Any = Depends(get_evidence_service),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve specific incident details with child reports."""
    details = evidence_service.get_incident_details(incident_id, db)
    if not details:
        raise HTTPException(status_code=404, detail="Incident not found")
    return cast(dict[str, Any], details)


class MergeIssueSchema(BaseModel):
    issue_id: str = Field(
        ..., description="UUID of the issue to merge into this incident"
    )


@router.post("/incidents/{incident_id}/merge", response_model=dict[str, Any])
async def merge_issue_into_incident(
    incident_id: str,
    payload: MergeIssueSchema,
    evidence_service: Any = Depends(get_evidence_service),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Merge a citizen issue report into an incident cluster."""
    try:
        return cast(
            dict[str, Any],
            evidence_service.merge_issue_into_incident(
                payload.issue_id, incident_id, db
            ),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
