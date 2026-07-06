import uuid

from sqlalchemy.orm import Session

from services.governance.infrastructure.models import IssueDB, RecommendationDB
from shared.domain.entities import Issue, Recommendation
from shared.domain.enums import IssueStatus, Priority, RecommendationStatus
from shared.domain.repositories import (
    IssueRepository,
    NotificationRepository,
    RecommendationRepository,
)
from shared.domain.value_objects import Location


class SQLAlchemyIssueRepository(IssueRepository):
    """SQLAlchemy implementation of the Issue Repository interface."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, issue: Issue) -> None:
        db_issue = self.db.query(IssueDB).filter(IssueDB.id == str(issue.id)).first()
        if not db_issue:
            db_issue = IssueDB(id=str(issue.id))
            self.db.add(db_issue)

        db_issue.citizen_id = str(issue.citizen_id)
        db_issue.title = issue.title
        db_issue.description = issue.description
        db_issue.category = issue.category
        db_issue.location_address = issue.location.formatted_address
        db_issue.latitude = issue.location.latitude
        db_issue.longitude = issue.location.longitude
        db_issue.status = issue.status.name
        db_issue.priority = issue.priority.name if issue.priority else "LOW"
        db_issue.department_id = (
            str(issue.department_id) if issue.department_id else None
        )
        self.db.commit()

    def get_by_id(self, issue_id: uuid.UUID) -> Issue | None:
        db_issue = self.db.query(IssueDB).filter(IssueDB.id == str(issue_id)).first()
        if not db_issue:
            return None

        loc = Location(
            latitude=db_issue.latitude,
            longitude=db_issue.longitude,
            formatted_address=db_issue.location_address,
        )

        return Issue(
            id=uuid.UUID(db_issue.id),
            citizen_id=uuid.UUID(db_issue.citizen_id),
            title=db_issue.title,
            description=db_issue.description,
            category=db_issue.category,
            location=loc,
            status=IssueStatus[db_issue.status],
            priority=Priority[db_issue.priority] if db_issue.priority else None,
            department_id=(
                uuid.UUID(db_issue.department_id) if db_issue.department_id else None
            ),
        )


class SQLAlchemyRecommendationRepository(RecommendationRepository):
    """SQLAlchemy implementation of the Recommendation Repository interface."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def save(
        self,
        recommendation: Recommendation,
        suggested_category: str | None = None,
        suggested_department: str | None = None,
        confidence_score: float | None = None,
    ) -> None:
        db_rec = (
            self.db.query(RecommendationDB)
            .filter(RecommendationDB.id == str(recommendation.id))
            .first()
        )
        if not db_rec:
            db_rec = RecommendationDB(id=str(recommendation.id))
            self.db.add(db_rec)

        db_rec.issue_id = str(recommendation.issue_id)
        db_rec.suggested_category = suggested_category or "general"
        db_rec.suggested_department = suggested_department or "Public Works"
        db_rec.confidence_score = confidence_score or 1.0
        db_rec.rationale = recommendation.content
        db_rec.status = recommendation.status.name
        self.db.commit()

    def get_by_id(self, recommendation_id: uuid.UUID) -> Recommendation | None:
        db_rec = (
            self.db.query(RecommendationDB)
            .filter(RecommendationDB.id == str(recommendation_id))
            .first()
        )
        if not db_rec:
            return None

        # Map back to domain aggregate (which expects at least one evidence ID)
        return Recommendation(
            id=uuid.UUID(db_rec.id),
            issue_id=uuid.UUID(db_rec.issue_id),
            evidence_ids=[uuid.uuid4()],  # In Sprint 2 we mock the evidence list
            content=db_rec.rationale,
            status=RecommendationStatus[db_rec.status],
        )

    def get_by_issue_id(self, issue_id: uuid.UUID) -> Recommendation | None:
        db_rec = (
            self.db.query(RecommendationDB)
            .filter(RecommendationDB.issue_id == str(issue_id))
            .first()
        )
        if not db_rec:
            return None

        return Recommendation(
            id=uuid.UUID(db_rec.id),
            issue_id=uuid.UUID(db_rec.issue_id),
            evidence_ids=[uuid.uuid4()],
            content=db_rec.rationale,
            status=RecommendationStatus[db_rec.status],
        )


class LogNotificationRepository(NotificationRepository):
    """Notification implementation that logs outgoing SMS messages."""

    def notify(self, citizen_id: uuid.UUID, message: str) -> None:
        from helix_platform.logging import get_logger

        logger = get_logger("notifications")
        logger.info(
            "sms_notification_sent",
            recipient="Citizen",
            citizen_id=str(citizen_id),
            message=message,
        )
