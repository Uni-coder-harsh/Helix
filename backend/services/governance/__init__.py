import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from helix_platform.event_bus import EventBus
from helix_platform.logging import get_logger
from helix_platform.persistence import get_db
from services.governance.models import IssueDB, RecommendationDB
from shared.domain.events import (
    IssueIngestedEvent,
    RecommendationAcceptedEvent,
    RecommendationRejectedEvent,
)

logger = get_logger("governance_api")
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
        default="No reason provided",
        description="Reason for rejection or verification notes",
    )


@router.get("")
@router.get("/")
async def get_root() -> dict[str, str]:
    """Governance Service status endpoint."""
    return {"service": "Governance Service", "status": "active"}


@router.post("/issues", response_model=dict[str, Any])
async def submit_issue(
    payload: IssueCreateSchema, db: Session = Depends(get_db)
) -> dict[str, Any]:
    """1. Citizen submits an issue, triggering the ingestion pipeline."""
    logger.info(
        "submit_issue_received", title=payload.title, citizen_id=payload.citizen_id
    )

    # 1. Map to Database Entity
    issue_id = str(uuid.uuid4())
    db_issue = IssueDB(
        id=issue_id,
        citizen_id=payload.citizen_id,
        title=payload.title,
        description=payload.description,
        category=payload.category,
        location_address=payload.formatted_address,
        latitude=payload.latitude,
        longitude=payload.longitude,
        status="INTAKE",
        priority="LOW",
    )

    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)

    logger.info("issue_persisted", issue_id=issue_id)

    # 2. Publish Domain Event to trigger workflows
    ingested_event = IssueIngestedEvent(
        issue_id=uuid.UUID(issue_id),
        citizen_id=uuid.UUID(payload.citizen_id),
        title=payload.title,
        category=payload.category,
        location_address=payload.formatted_address,
    )
    EventBus.publish(ingested_event)

    return {"issue_id": issue_id, "status": "INTAKE"}


@router.get("/issues/pending", response_model=list[dict[str, Any]])
async def list_pending_issues(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """List pending issues waiting for triage or AI recommendation review."""
    issues = db.query(IssueDB).all()
    result = []
    for issue in issues:
        # Find if there is a recommendation associated with this issue
        rec = (
            db.query(RecommendationDB)
            .filter(RecommendationDB.issue_id == issue.id)
            .first()
        )
        result.append(
            {
                "id": issue.id,
                "citizen_id": issue.citizen_id,
                "title": issue.title,
                "description": issue.description,
                "category": issue.category,
                "status": issue.status,
                "priority": issue.priority,
                "location_address": issue.location_address,
                "latitude": issue.latitude,
                "longitude": issue.longitude,
                "created_at": (
                    issue.created_at.isoformat() if issue.created_at else None
                ),
                "has_recommendation": rec is not None,
                "recommendation_id": rec.id if rec else None,
            }
        )
    return result


@router.get("/recommendations/{issue_id}", response_model=dict[str, Any])
async def get_recommendation(
    issue_id: str, db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Retrieve the AI recommendation for a specific issue."""
    rec = (
        db.query(RecommendationDB).filter(RecommendationDB.issue_id == issue_id).first()
    )
    if not rec:
        raise HTTPException(
            status_code=404, detail="AI recommendation not found for this issue."
        )
    return {
        "id": rec.id,
        "issue_id": rec.issue_id,
        "suggested_category": rec.suggested_category,
        "suggested_department": rec.suggested_department,
        "confidence_score": rec.confidence_score,
        "rationale": rec.rationale,
        "status": rec.status,
    }


@router.post(
    "/recommendations/{recommendation_id}/accept", response_model=dict[str, Any]
)
async def accept_recommendation(
    recommendation_id: str, db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Approve the AI recommendation, assigning the task and transitioning the issue state."""
    rec = (
        db.query(RecommendationDB)
        .filter(RecommendationDB.id == recommendation_id)
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found.")

    rec.status = "ACCEPTED"

    # Transition the associated Issue status
    issue = db.query(IssueDB).filter(IssueDB.id == rec.issue_id).first()
    if issue:
        issue.status = "ASSIGNED"

    db.commit()
    logger.info(
        "ai_recommendation_accepted",
        recommendation_id=recommendation_id,
        issue_id=rec.issue_id,
    )

    # Publish RecommendationAcceptedEvent
    decision_id = uuid.uuid4()
    accepted_event = RecommendationAcceptedEvent(
        recommendation_id=uuid.UUID(recommendation_id),
        decision_id=decision_id,
    )
    EventBus.publish(accepted_event)

    return {
        "status": "SUCCESS",
        "decision_id": str(decision_id),
        "new_issue_status": "ASSIGNED",
    }


@router.post(
    "/recommendations/{recommendation_id}/reject", response_model=dict[str, Any]
)
async def reject_recommendation(
    recommendation_id: str,
    payload: RecommendationVerdictSchema,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Reject the AI recommendation."""
    rec = (
        db.query(RecommendationDB)
        .filter(RecommendationDB.id == recommendation_id)
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found.")

    rec.status = "REJECTED"

    # Transition the associated Issue status
    issue = db.query(IssueDB).filter(IssueDB.id == rec.issue_id).first()
    if issue:
        issue.status = "REJECTED"

    db.commit()
    logger.info(
        "ai_recommendation_rejected",
        recommendation_id=recommendation_id,
        issue_id=rec.issue_id,
    )

    # Publish RecommendationRejectedEvent
    rejected_event = RecommendationRejectedEvent(
        recommendation_id=uuid.UUID(recommendation_id),
        reason=payload.reason,
    )
    EventBus.publish(rejected_event)

    return {"status": "SUCCESS", "new_issue_status": "REJECTED"}


@router.get("/dashboard/stats", response_model=dict[str, int])
async def get_dashboard_stats(db: Session = Depends(get_db)) -> dict[str, int]:
    """Compute summary statistics for issues grouped by status mapping."""
    issues = db.query(IssueDB).all()
    stats = {
        "PENDING": 0,  # INTAKE, TRIAGE
        "APPROVED": 0,  # ASSIGNED
        "REJECTED": 0,  # REJECTED
        "RESOLVED": 0,  # RESOLVED, CLOSED
    }
    for issue in issues:
        status = issue.status.upper()
        if status in ["INTAKE", "TRIAGE"]:
            stats["PENDING"] += 1
        elif status in ["ASSIGNED"]:
            stats["APPROVED"] += 1
        elif status in ["REJECTED"]:
            stats["REJECTED"] += 1
        elif status in ["RESOLVED", "CLOSED"]:
            stats["RESOLVED"] += 1

    return stats
