import uuid

from helix_platform.event_bus import EventBus
from shared.domain.entities import Issue, Recommendation
from shared.domain.enums import IssueStatus, Priority
from shared.domain.events import (
    IssueIngestedEvent,
    IssueTriagedEvent,
    RecommendationAcceptedEvent,
    RecommendationProposedEvent,
    RecommendationRejectedEvent,
)
from shared.domain.repositories import (
    IssueRepository,
    NotificationRepository,
    RecommendationRepository,
)
from shared.domain.value_objects import Location


class TriageDecisionPolicy:
    """Policy engine that evaluates triage criteria for incoming complaints."""

    @staticmethod
    def evaluate(category: str) -> Priority:
        cat_lower = category.lower()
        if "sanitation" in cat_lower or "garbage" in cat_lower:
            return Priority.HIGH
        if "road" in cat_lower or "pothole" in cat_lower or "traffic" in cat_lower:
            return Priority.MEDIUM
        return Priority.LOW


class IssueApplicationService:
    """Application Service handling issue intake and lifecycle orchestration."""

    def __init__(self, issue_repo: IssueRepository) -> None:
        self.issue_repo = issue_repo

    async def ingest_issue(
        self,
        citizen_id: uuid.UUID,
        title: str,
        description: str,
        category: str,
        latitude: float,
        longitude: float,
        formatted_address: str,
    ) -> str:
        issue_id = uuid.uuid4()
        location = Location(
            latitude=latitude,
            longitude=longitude,
            formatted_address=formatted_address,
        )

        # Create Domain Aggregate
        issue = Issue(
            id=issue_id,
            citizen_id=citizen_id,
            title=title,
            description=description,
            category=category,
            location=location,
            status=IssueStatus.INGESTED,
        )

        # Persist Domain Aggregate state via repository
        self.issue_repo.save(issue)

        # Publish Event to trigger workflow async triage
        event = IssueIngestedEvent(
            issue_id=issue_id,
            citizen_id=citizen_id,
            title=title,
            category=category,
            location_address=formatted_address,
        )
        EventBus.publish(event)

        return str(issue_id)

    async def triage_issue(
        self,
        issue_id: uuid.UUID,
        department_id: uuid.UUID,
        priority: Priority,
    ) -> None:
        """Triage an ingested issue, assigning priority and department."""
        issue = self.issue_repo.get_by_id(issue_id)
        if not issue:
            raise ValueError(f"Issue not found: {issue_id}")

        # Call state transition on Domain aggregate
        issue.triage(department_id, priority)

        # Save state
        self.issue_repo.save(issue)

        # Publish Event
        triage_event = IssueTriagedEvent(
            issue_id=issue_id,
            department_id=department_id,
            priority=priority,
        )
        EventBus.publish(triage_event)


class RecommendationApplicationService:
    """Application Service coordinating AI Recommendations logic."""

    def __init__(self, rec_repo: RecommendationRepository) -> None:
        self.rec_repo = rec_repo

    async def propose_recommendation(
        self,
        issue_id: uuid.UUID,
        category: str,
        department: str,
        confidence: float,
        rationale: str,
    ) -> str:
        rec_id = uuid.uuid4()

        # Create Recommendation Domain Aggregate
        rec = Recommendation(
            id=rec_id,
            issue_id=issue_id,
            evidence_ids=[uuid.uuid4()],  # Mock backing evidence link
            content=rationale,
        )

        # Persist Recommendation via repository
        self.rec_repo.save(
            recommendation=rec,
            suggested_category=category,
            suggested_department=department,
            confidence_score=confidence,
        )

        # Publish Event
        event = RecommendationProposedEvent(
            recommendation_id=rec_id,
            issue_id=issue_id,
            content=rationale,
        )
        EventBus.publish(event)

        return str(rec_id)


class OfficerApplicationService:
    """Application Service orchestrating Officer verification triage decisions."""

    def __init__(
        self,
        issue_repo: IssueRepository,
        rec_repo: RecommendationRepository,
        notification_repo: NotificationRepository,
    ) -> None:
        self.issue_repo = issue_repo
        self.rec_repo = rec_repo
        self.notification_repo = notification_repo

    async def accept_recommendation(self, rec_id: uuid.UUID) -> str:
        rec = self.rec_repo.get_by_id(rec_id)
        if not rec:
            raise ValueError(f"AI recommendation not found: {rec_id}")

        issue = self.issue_repo.get_by_id(rec.issue_id)
        if not issue:
            raise ValueError(f"Associated issue not found: {rec.issue_id}")

        decision_id = uuid.uuid4()

        # Call state transition on Domain aggregates
        rec.accept(decision_id)

        # Call domain aggregate method to add task, which advances status to IN_PROGRESS
        issue.add_task(
            task_id=decision_id, title="Dispatched task based on AI recommendation"
        )

        # Save both aggregates
        self.rec_repo.save(rec)
        self.issue_repo.save(issue)

        # Disperse Event
        event = RecommendationAcceptedEvent(
            recommendation_id=rec_id,
            decision_id=decision_id,
        )
        EventBus.publish(event)

        # Send transparent notification SMS
        self.notification_repo.notify(
            citizen_id=issue.citizen_id,
            message=f"Your issue has been approved. Task ID: {decision_id}.",
        )

        return str(decision_id)

    async def reject_recommendation(self, rec_id: uuid.UUID, reason: str) -> None:
        rec = self.rec_repo.get_by_id(rec_id)
        if not rec:
            raise ValueError(f"AI recommendation not found: {rec_id}")

        issue = self.issue_repo.get_by_id(rec.issue_id)
        if not issue:
            raise ValueError(f"Associated issue not found: {rec.issue_id}")

        # Call reject state transition on aggregate
        rec.reject(reason)
        issue._status = IssueStatus.INGESTED  # Revert back to INTAKE

        self.rec_repo.save(rec)
        self.issue_repo.save(issue)

        event = RecommendationRejectedEvent(
            recommendation_id=rec_id,
            reason=reason,
        )
        EventBus.publish(event)

        self.notification_repo.notify(
            citizen_id=issue.citizen_id,
            message=f"Your recommendation was rejected. Reason: {reason}.",
        )
