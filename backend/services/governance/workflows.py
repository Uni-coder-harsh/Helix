import uuid

from helix_platform.event_bus import EventBus
from helix_platform.logging import get_logger
from helix_platform.persistence import SessionLocal

# Domain, Query, Repositories, Services
from services.governance.application.services import (
    IssueApplicationService,
    RecommendationApplicationService,
    TriageDecisionPolicy,
)
from services.governance.infrastructure.repositories import (
    SQLAlchemyIssueRepository,
    SQLAlchemyRecommendationRepository,
)
from shared.domain.enums import Priority
from shared.domain.events import (
    IssueIngestedEvent,
    IssueTriagedEvent,
    RecommendationAcceptedEvent,
    RecommendationRejectedEvent,
)

logger = get_logger("workflows")


async def handle_issue_ingested(event: IssueIngestedEvent) -> None:
    """Workflow handler for automated issue triage upon ingestion."""
    logger.info("handling_issue_ingested", issue_id=str(event.issue_id))

    # 1. Evaluate Decision Policy to obtain Priority Heuristics
    priority = TriageDecisionPolicy.evaluate(event.category)
    department_id = uuid.uuid4()  # Mock department assignment

    # 2. Invoke Application Service to transition and save state
    db = SessionLocal()
    try:
        repo = SQLAlchemyIssueRepository(db)
        service = IssueApplicationService(repo)
        await service.triage_issue(event.issue_id, department_id, priority)
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

    # Load issue category from repository to simulate policy RAG/Rules
    db = SessionLocal()
    try:
        issue_repo = SQLAlchemyIssueRepository(db)
        issue = issue_repo.get_by_id(event.issue_id)
        if not issue:
            return

        category = issue.category
        suggested_dept = (
            "Municipal Sanitation Department"
            if category == "sanitation"
            else "Public Works Department"
        )
        confidence = 0.90 if event.priority == Priority.HIGH else 0.75

        rationale = (
            f"Based on governance policies for Category: {category}. "
            f"Standard resolution timeline requires dispatch within 48 hours."
        )

        # Invoke Application Service to propose and save recommendation
        rec_repo = SQLAlchemyRecommendationRepository(db)
        rec_service = RecommendationApplicationService(rec_repo)
        await rec_service.propose_recommendation(
            issue_id=event.issue_id,
            category=category,
            department=suggested_dept,
            confidence=confidence,
            rationale=rationale,
        )
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
