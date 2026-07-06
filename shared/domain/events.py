import uuid

from shared.domain.base import DomainEvent
from shared.domain.enums import Priority


class CitizenRegisteredEvent(DomainEvent):
    def __init__(self, citizen_id: uuid.UUID, name: str, email: str) -> None:
        super().__init__()
        self.citizen_id = citizen_id
        self.name = name
        self.email = email


class CitizenDeactivatedEvent(DomainEvent):
    def __init__(self, citizen_id: uuid.UUID, reason: str) -> None:
        super().__init__()
        self.citizen_id = citizen_id
        self.reason = reason


class IssueIngestedEvent(DomainEvent):
    def __init__(
        self,
        issue_id: uuid.UUID,
        citizen_id: uuid.UUID,
        title: str,
        category: str,
        location_address: str,
    ) -> None:
        super().__init__()
        self.issue_id = issue_id
        self.citizen_id = citizen_id
        self.title = title
        self.category = category
        self.location_address = location_address


class IssueTriagedEvent(DomainEvent):
    def __init__(
        self, issue_id: uuid.UUID, department_id: uuid.UUID, priority: Priority
    ) -> None:
        super().__init__()
        self.issue_id = issue_id
        self.department_id = department_id
        self.priority = priority


class IssueInProgressEvent(DomainEvent):
    def __init__(self, issue_id: uuid.UUID) -> None:
        super().__init__()
        self.issue_id = issue_id


class IssueResolvedEvent(DomainEvent):
    def __init__(self, issue_id: uuid.UUID, resolution_notes: str) -> None:
        super().__init__()
        self.issue_id = issue_id
        self.resolution_notes = resolution_notes


class IssueClosedEvent(DomainEvent):
    def __init__(self, issue_id: uuid.UUID, feedback_score: int | None = None) -> None:
        super().__init__()
        self.issue_id = issue_id
        self.feedback_score = feedback_score


class TaskCreatedEvent(DomainEvent):
    def __init__(
        self,
        task_id: uuid.UUID,
        issue_id: uuid.UUID,
        title: str,
        department_id: uuid.UUID,
    ) -> None:
        super().__init__()
        self.task_id = task_id
        self.issue_id = issue_id
        self.title = title
        self.department_id = department_id


class TaskAssignedEvent(DomainEvent):
    def __init__(self, task_id: uuid.UUID, officer_id: uuid.UUID) -> None:
        super().__init__()
        self.task_id = task_id
        self.officer_id = officer_id


class TaskCompletedEvent(DomainEvent):
    def __init__(self, task_id: uuid.UUID, completion_notes: str) -> None:
        super().__init__()
        self.task_id = task_id
        self.completion_notes = completion_notes


class TaskVerifiedEvent(DomainEvent):
    def __init__(self, task_id: uuid.UUID, verified_by: uuid.UUID) -> None:
        super().__init__()
        self.task_id = task_id
        self.verified_by = verified_by


class ProjectPlannedEvent(DomainEvent):
    def __init__(
        self, project_id: uuid.UUID, title: str, representative_id: uuid.UUID
    ) -> None:
        super().__init__()
        self.project_id = project_id
        self.title = title
        self.representative_id = representative_id


class ProjectApprovedEvent(DomainEvent):
    def __init__(self, project_id: uuid.UUID, approved_by: uuid.UUID) -> None:
        super().__init__()
        self.project_id = project_id
        self.approved_by = approved_by


class ProjectActivatedEvent(DomainEvent):
    def __init__(self, project_id: uuid.UUID) -> None:
        super().__init__()
        self.project_id = project_id


class ProjectCompletedEvent(DomainEvent):
    def __init__(self, project_id: uuid.UUID, completion_summary: str) -> None:
        super().__init__()
        self.project_id = project_id
        self.completion_summary = completion_summary


class SchemeProposedEvent(DomainEvent):
    def __init__(
        self, scheme_id: uuid.UUID, title: str, department_id: uuid.UUID
    ) -> None:
        super().__init__()
        self.scheme_id = scheme_id
        self.title = title
        self.department_id = department_id


class SchemeActivatedEvent(DomainEvent):
    def __init__(self, scheme_id: uuid.UUID) -> None:
        super().__init__()
        self.scheme_id = scheme_id


class SchemeExpiredEvent(DomainEvent):
    def __init__(self, scheme_id: uuid.UUID) -> None:
        super().__init__()
        self.scheme_id = scheme_id


class EvidenceExtractedEvent(DomainEvent):
    def __init__(
        self, evidence_id: uuid.UUID, source_type: str, source_id: uuid.UUID
    ) -> None:
        super().__init__()
        self.evidence_id = evidence_id
        self.source_type = source_type
        self.source_id = source_id


class RecommendationProposedEvent(DomainEvent):
    def __init__(
        self, recommendation_id: uuid.UUID, issue_id: uuid.UUID, content: str
    ) -> None:
        super().__init__()
        self.recommendation_id = recommendation_id
        self.issue_id = issue_id
        self.content = content


class RecommendationAcceptedEvent(DomainEvent):
    def __init__(self, recommendation_id: uuid.UUID, decision_id: uuid.UUID) -> None:
        super().__init__()
        self.recommendation_id = recommendation_id
        self.decision_id = decision_id


class RecommendationRejectedEvent(DomainEvent):
    def __init__(self, recommendation_id: uuid.UUID, reason: str) -> None:
        super().__init__()
        self.recommendation_id = recommendation_id
        self.reason = reason


class DepartmentCreatedEvent(DomainEvent):
    def __init__(self, department_id: uuid.UUID, name: str) -> None:
        super().__init__()
        self.department_id = department_id
        self.name = name


class DepartmentMergedEvent(DomainEvent):
    def __init__(
        self, department_id: uuid.UUID, target_department_id: uuid.UUID
    ) -> None:
        super().__init__()
        self.department_id = department_id
        self.target_department_id = target_department_id


class DepartmentArchivedEvent(DomainEvent):
    def __init__(self, department_id: uuid.UUID) -> None:
        super().__init__()
        self.department_id = department_id


class OutcomeRecordedEvent(DomainEvent):
    def __init__(
        self,
        outcome_id: uuid.UUID,
        target_id: uuid.UUID,
        metric_name: str,
        score: float,
    ) -> None:
        super().__init__()
        self.outcome_id = outcome_id
        self.target_id = target_id
        self.metric_name = metric_name
        self.score = score


class OutcomeVerifiedEvent(DomainEvent):
    def __init__(self, outcome_id: uuid.UUID, verified_by: uuid.UUID) -> None:
        super().__init__()
        self.outcome_id = outcome_id
        self.verified_by = verified_by
