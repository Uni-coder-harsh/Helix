import uuid

from helix_platform.event_bus import EventBus
from helix_platform.logging import get_logger
from helix_platform.persistence import SessionLocal
from services.governance.models import IssueDB, RecommendationDB
from shared.domain.enums import Priority
from shared.domain.events import (
    IssueIngestedEvent,
    IssueTriagedEvent,
    RecommendationAcceptedEvent,
    RecommendationProposedEvent,
    RecommendationRejectedEvent,
)

logger = get_logger("workflows")


async def handle_issue_ingested(event: IssueIngestedEvent) -> None:
    """Workflow handler for automated issue triage upon ingestion."""
    logger.info("handling_issue_ingested", issue_id=str(event.issue_id))
    db = SessionLocal()
    try:
        issue = db.query(IssueDB).filter(IssueDB.id == str(event.issue_id)).first()
        if not issue:
            logger.warning("issue_not_found_for_triage", issue_id=str(event.issue_id))
            return

        # Perform automatic triage rules
        issue.status = "TRIAGE"

        # Priority Rule heuristics
        cat_lower = issue.category.lower()
        if "sanitation" in cat_lower or "garbage" in cat_lower:
            issue.priority = "HIGH"
        elif "road" in cat_lower or "pothole" in cat_lower or "traffic" in cat_lower:
            issue.priority = "MEDIUM"
        else:
            issue.priority = "LOW"

        db.commit()
        logger.info(
            "issue_triaged_automatically",
            issue_id=issue.id,
            priority=issue.priority,
        )

        # Trigger transition: publish IssueTriagedEvent
        # (representing validated/triaged state)
        triage_event = IssueTriagedEvent(
            issue_id=uuid.UUID(issue.id),
            department_id=uuid.uuid4(),  # Mock department assignment
            priority=Priority(issue.priority),
        )
        EventBus.publish(triage_event)
    finally:
        db.close()


async def handle_issue_triaged(event: IssueTriagedEvent) -> None:
    """AI listener that automatically generates recommendations.

    Runs for triaged issues.
    """
    logger.info(
        "handling_issue_triaged_for_recommendation",
        issue_id=str(event.issue_id),
    )
    db = SessionLocal()
    try:
        issue = db.query(IssueDB).filter(IssueDB.id == str(event.issue_id)).first()
        if not issue:
            return

        # Simulate RAG / Policy and recommendation generation
        category = issue.category
        suggested_dept = (
            "Municipal Sanitation Department"
            if category == "sanitation"
            else "Public Works Department"
        )
        confidence = 0.90 if issue.priority == "HIGH" else 0.75

        rationale = (
            f"Based on governance policies for Category: {category}. "
            f"Standard resolution timeline requires dispatch within 48 hours."
        )

        # Persist Recommendation
        rec = RecommendationDB(
            id=str(uuid.uuid4()),
            issue_id=issue.id,
            suggested_category=category,
            suggested_department=suggested_dept,
            confidence_score=confidence,
            rationale=rationale,
            status="PROPOSED",
        )
        db.add(rec)
        db.commit()
        logger.info(
            "ai_recommendation_generated",
            recommendation_id=rec.id,
            issue_id=issue.id,
        )

        # Publish recommendation proposed event
        proposed_event = RecommendationProposedEvent(
            recommendation_id=uuid.UUID(rec.id),
            issue_id=uuid.UUID(issue.id),
            content=rationale,
        )
        EventBus.publish(proposed_event)
    finally:
        db.close()


async def handle_recommendation_accepted(event: RecommendationAcceptedEvent) -> None:
    """Mock notification dispatch handler for accepted recommendations."""
    msg = f"Your issue has been approved. Task dispatched (ID: {event.decision_id})."
    logger.info("sms_notification_sent", recipient="Citizen", message=msg)


async def handle_recommendation_rejected(event: RecommendationRejectedEvent) -> None:
    """Mock notification dispatch handler for rejected recommendations."""
    msg = f"Your recommendation was rejected. Reason: {event.reason}."
    logger.info("sms_notification_sent", recipient="Citizen", message=msg)


def register_subscriptions() -> None:
    """Subscribe workflow and recommendation handlers to the EventBus."""
    EventBus.subscribe(IssueIngestedEvent, handle_issue_ingested)
    EventBus.subscribe(IssueTriagedEvent, handle_issue_triaged)
    EventBus.subscribe(RecommendationAcceptedEvent, handle_recommendation_accepted)
    EventBus.subscribe(RecommendationRejectedEvent, handle_recommendation_rejected)
