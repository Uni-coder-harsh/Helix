import uuid

from helix_platform.event_bus import EventBus
from helix_platform.logging import get_logger
from helix_platform.persistence import SessionLocal
from services.governance.application.intelligence import RecommendationBuilder
from services.governance.application.knowledge_service import KnowledgeService

# Domain, Query, Repositories, Services
from services.governance.application.services import (
    IssueApplicationService,
    RecommendationApplicationService,
    TriageDecisionPolicy,
)

# Knowledge Layer & Governance Intelligence Engine
from services.governance.infrastructure.knowledge.stores import (
    InMemoryAdministrativeHierarchy,
    InMemoryAssetStore,
    InMemoryDepartmentStore,
    InMemoryKnowledgeSearch,
    InMemoryPolicyStore,
    InMemorySchemeStore,
)
from services.governance.infrastructure.repositories import (
    SQLAlchemyIssueRepository,
    SQLAlchemyRecommendationRepository,
)
from shared.domain.events import (
    IssueIngestedEvent,
    IssueTriagedEvent,
    RecommendationAcceptedEvent,
    RecommendationRejectedEvent,
)

logger = get_logger("workflows")

# Initialize unified knowledge dependencies
policy_store = InMemoryPolicyStore()
scheme_store = InMemorySchemeStore()
asset_store = InMemoryAssetStore()
hierarchy_store = InMemoryAdministrativeHierarchy()
dept_store = InMemoryDepartmentStore()
search_engine = InMemoryKnowledgeSearch(policy_store, scheme_store, asset_store)

knowledge_service = KnowledgeService(
    policies=policy_store,
    schemes=scheme_store,
    assets=asset_store,
    hierarchy=hierarchy_store,
    departments=dept_store,
    search=search_engine,
)

rec_builder = RecommendationBuilder(knowledge_service)


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

        # Build explainable recommendation using our new Governance Intelligence Engine
        rec_details = await rec_builder.build_recommendation(
            issue_id=event.issue_id,
            category=issue.category,
            latitude=issue.location.latitude,
            longitude=issue.location.longitude,
        )

        # Invoke Application Service to propose and save recommendation
        rec_repo = SQLAlchemyRecommendationRepository(db)
        rec_service = RecommendationApplicationService(rec_repo)
        await rec_service.propose_recommendation(
            issue_id=event.issue_id,
            category=issue.category,
            department=rec_details["suggested_department"],
            confidence=rec_details["confidence"],
            rationale=rec_details["reasoning_chain"],
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
