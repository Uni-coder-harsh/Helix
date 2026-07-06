import uuid
from typing import Any

from sqlalchemy.orm import Session

from services.governance.application.queries import GovernanceQueryService
from services.governance.infrastructure.models import IssueDB, RecommendationDB


class SQLAlchemyGovernanceQueryService(GovernanceQueryService):
    """SQLAlchemy-backed implementation of CQRS read query operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_pending_issues(self) -> list[dict[str, Any]]:
        issues = self.db.query(IssueDB).all()
        result = []
        for issue in issues:
            rec = (
                self.db.query(RecommendationDB)
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

    def get_recommendation_details(self, issue_id: uuid.UUID) -> dict[str, Any]:
        rec = (
            self.db.query(RecommendationDB)
            .filter(RecommendationDB.issue_id == str(issue_id))
            .first()
        )
        if not rec:
            raise KeyError(f"AI recommendation not found for issue: {issue_id}")
        return {
            "id": rec.id,
            "issue_id": rec.issue_id,
            "suggested_category": rec.suggested_category,
            "suggested_department": rec.suggested_department,
            "confidence_score": rec.confidence_score,
            "rationale": rec.rationale,
            "status": rec.status,
        }

    def get_dashboard_stats(self) -> dict[str, int]:
        issues = self.db.query(IssueDB).all()
        stats = {
            "PENDING": 0,  # INTAKE, TRIAGE
            "APPROVED": 0,  # ASSIGNED
            "REJECTED": 0,  # REJECTED
            "RESOLVED": 0,  # RESOLVED, CLOSED
        }
        for issue in issues:
            status = issue.status.upper()
            if status in ["INTAKE", "TRIAGE", "INGESTED", "TRIAGED"]:
                stats["PENDING"] += 1
            elif status in ["ASSIGNED", "IN_PROGRESS"]:
                stats["APPROVED"] += 1
            elif status in ["REJECTED"]:
                stats["REJECTED"] += 1
            elif status in ["RESOLVED", "CLOSED"]:
                stats["RESOLVED"] += 1

        return stats
