import uuid
from typing import Any

from sqlalchemy.orm import Session

from services.governance.infrastructure.models import IncidentDB, IssueDB

from .clustering import ClusteringEngine
from .duplicate_detector import DuplicateDetector


class EvidenceIntelligenceService:
    """Core evidence service managing duplicate detection, incidents, and merges."""

    def __init__(self, match_threshold: float = 0.70):
        self.detector = DuplicateDetector()
        self.engine = ClusteringEngine(match_threshold=match_threshold)

    def get_issue_duplicates(self, issue_id: str, db: Session) -> list[dict[str, Any]]:
        """Finds all issues that are potential duplicates of the target issue."""
        target = db.query(IssueDB).filter(IssueDB.id == issue_id).first()
        if not target:
            return []

        target_dict = self._to_dict(target)
        all_issues = db.query(IssueDB).filter(IssueDB.id != issue_id).all()

        duplicates = []
        for issue in all_issues:
            # If they are already linked to the same incident, they are duplicates
            if target.incident_id and issue.incident_id == target.incident_id:
                conf, breakdown = self.detector.calculate_confidence(
                    target_dict, self._to_dict(issue)
                )
                duplicates.append(
                    {
                        "issue": self._to_dict(issue),
                        "confidence": 1.0,
                        "breakdown": breakdown,
                        "already_merged": True,
                    }
                )
                continue

            conf, breakdown = self.detector.calculate_confidence(
                target_dict, self._to_dict(issue)
            )
            if conf >= self.engine.match_threshold:
                duplicates.append(
                    {
                        "issue": self._to_dict(issue),
                        "confidence": conf,
                        "breakdown": breakdown,
                        "already_merged": False,
                    }
                )

        # Sort by confidence descending
        duplicates.sort(key=lambda x: float(x["confidence"]), reverse=True)
        return duplicates

    def get_all_incidents(self, db: Session) -> list[dict[str, Any]]:
        """Retrieves all clustered incidents, including their citizen report counts."""
        incidents = db.query(IncidentDB).all()
        result = []
        for inc in incidents:
            reports_count = (
                db.query(IssueDB).filter(IssueDB.incident_id == str(inc.id)).count()
            )
            d = self._to_dict(inc)
            d["reports_count"] = reports_count
            result.append(d)
        return result

    def get_incident_details(
        self, incident_id: str, db: Session
    ) -> dict[str, Any] | None:
        """Retrieves specific incident metadata along with all its child reports."""
        inc = db.query(IncidentDB).filter(IncidentDB.id == incident_id).first()
        if not inc:
            return None

        result = self._to_dict(inc)
        reports = db.query(IssueDB).filter(IssueDB.incident_id == incident_id).all()
        result["reports"] = [self._to_dict(rep) for rep in reports]
        result["reports_count"] = len(reports)
        return result

    def merge_issue_into_incident(
        self, issue_id: str, incident_id: str, db: Session
    ) -> dict[str, Any]:
        """Manually merges a citizen issue report into an existing incident cluster."""
        issue = db.query(IssueDB).filter(IssueDB.id == issue_id).first()
        if not issue:
            raise ValueError(f"Issue {issue_id} not found.")

        incident = db.query(IncidentDB).filter(IncidentDB.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found.")

        issue.incident_id = incident_id
        db.commit()

        # Count reports
        reports_count = (
            db.query(IssueDB).filter(IssueDB.incident_id == incident_id).count()
        )

        return {
            "success": True,
            "issue_id": issue_id,
            "incident_id": incident_id,
            "reports_count": reports_count,
        }

    def auto_cluster_issue(self, issue_id: str, db: Session) -> dict[str, Any]:
        """Runs automatic duplicate clustering for a newly ingested issue."""
        issue = db.query(IssueDB).filter(IssueDB.id == issue_id).first()
        if not issue:
            raise ValueError(f"Issue {issue_id} not found.")

        # If already clustered, return immediately
        if issue.incident_id:
            return {
                "incident_id": issue.incident_id,
                "created_new": False,
                "confidence": 1.0,
            }

        issue_dict = self._to_dict(issue)
        incidents = db.query(IncidentDB).all()
        incidents_dicts = [self._to_dict(inc) for inc in incidents]

        # Map incident ID to its canonical issue (first registered issue in that incident)
        canonical_issues = {}
        for inc in incidents:
            canon = (
                db.query(IssueDB)
                .filter(IssueDB.incident_id == str(inc.id))
                .order_by(IssueDB.created_at.asc())
                .first()
            )
            if canon:
                canonical_issues[str(inc.id)] = self._to_dict(canon)

        matched_incident, conf, _breakdown = self.engine.find_best_incident_match(
            issue_dict, incidents_dicts, canonical_issues
        )

        if matched_incident:
            issue.incident_id = str(matched_incident["id"])
            db.commit()
            return {
                "incident_id": str(matched_incident["id"]),
                "created_new": False,
                "confidence": conf,
            }

        # Otherwise, create a new incident cluster
        new_incident = IncidentDB(
            id=str(uuid.uuid4()),
            title=f"Incident Cluster: {issue.title}",
            description=issue.description,
            category=issue.category,
            status="TRIAGED",
            latitude=issue.latitude,
            longitude=issue.longitude,
            location_address=issue.location_address,
        )
        db.add(new_incident)
        issue.incident_id = new_incident.id
        db.commit()

        return {"incident_id": new_incident.id, "created_new": True, "confidence": 1.0}

    def get_relationship_graph(self, db: Session) -> dict[str, list[dict[str, Any]]]:
        """Compiles a relational nodes-and-edges graph visualization of duplicate incidents."""
        incidents = db.query(IncidentDB).all()
        issues = db.query(IssueDB).all()

        nodes = []
        edges = []

        for inc in incidents:
            nodes.append(
                {
                    "id": str(inc.id),
                    "label": str(inc.title),
                    "type": "incident",
                    "category": str(inc.category),
                }
            )

        for issue in issues:
            nodes.append(
                {
                    "id": str(issue.id),
                    "label": str(issue.title),
                    "type": "issue",
                    "category": str(issue.category),
                }
            )

            if issue.incident_id:
                edges.append(
                    {
                        "source": str(issue.id),
                        "target": str(issue.incident_id),
                        "type": "belongs_to",
                    }
                )

        return {"nodes": nodes, "edges": edges}

    def _to_dict(self, model_obj: Any) -> dict[str, Any]:
        """Utility serialization helper."""
        if not model_obj:
            return {}
        result = {}
        for column in model_obj.__table__.columns:
            val = getattr(model_obj, column.name)
            if hasattr(val, "isoformat"):
                val = val.isoformat()
            result[column.name] = val
        return result
