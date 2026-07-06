import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from shared.domain.enums import Priority


@dataclass(frozen=True, kw_only=True)
class BaseCommand:
    command_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, kw_only=True)
class RegisterCitizenCommand(BaseCommand):
    citizen_id: uuid.UUID
    name: str
    email: str


@dataclass(frozen=True, kw_only=True)
class DeactivateCitizenCommand(BaseCommand):
    citizen_id: uuid.UUID
    reason: str


@dataclass(frozen=True, kw_only=True)
class IngestIssueCommand(BaseCommand):
    issue_id: uuid.UUID
    citizen_id: uuid.UUID
    title: str
    description: str
    category: str
    latitude: float
    longitude: float
    formatted_address: str
    attachment_urls: list[str] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True)
class TriageIssueCommand(BaseCommand):
    issue_id: uuid.UUID
    department_id: uuid.UUID
    priority: Priority


@dataclass(frozen=True, kw_only=True)
class CreateTaskCommand(BaseCommand):
    task_id: uuid.UUID
    issue_id: uuid.UUID
    title: str


@dataclass(frozen=True, kw_only=True)
class AssignTaskCommand(BaseCommand):
    issue_id: uuid.UUID
    task_id: uuid.UUID
    officer_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class CompleteTaskCommand(BaseCommand):
    issue_id: uuid.UUID
    task_id: uuid.UUID
    completion_notes: str


@dataclass(frozen=True, kw_only=True)
class VerifyTaskCommand(BaseCommand):
    issue_id: uuid.UUID
    task_id: uuid.UUID
    officer_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class ResolveIssueCommand(BaseCommand):
    issue_id: uuid.UUID
    resolution_notes: str


@dataclass(frozen=True, kw_only=True)
class CloseIssueCommand(BaseCommand):
    issue_id: uuid.UUID
    feedback_score: int | None = None


@dataclass(frozen=True, kw_only=True)
class PlanProjectCommand(BaseCommand):
    project_id: uuid.UUID
    title: str
    representative_id: uuid.UUID
    task_ids: list[uuid.UUID]
    asset_ids: list[uuid.UUID]


@dataclass(frozen=True, kw_only=True)
class ApproveProjectCommand(BaseCommand):
    project_id: uuid.UUID
    officer_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class ActivateProjectCommand(BaseCommand):
    project_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class CompleteProjectCommand(BaseCommand):
    project_id: uuid.UUID
    completion_summary: str


@dataclass(frozen=True, kw_only=True)
class ProposeSchemeCommand(BaseCommand):
    scheme_id: uuid.UUID
    department_id: uuid.UUID
    title: str


@dataclass(frozen=True, kw_only=True)
class ProposeRecommendationCommand(BaseCommand):
    recommendation_id: uuid.UUID
    issue_id: uuid.UUID
    evidence_ids: list[uuid.UUID]
    content: str


@dataclass(frozen=True, kw_only=True)
class AcceptRecommendationCommand(BaseCommand):
    recommendation_id: uuid.UUID
    decision_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class RecordOutcomeCommand(BaseCommand):
    outcome_id: uuid.UUID
    target_id: uuid.UUID
    metric_name: str
    score: float


@dataclass(frozen=True, kw_only=True)
class VerifyOutcomeCommand(BaseCommand):
    outcome_id: uuid.UUID
    officer_id: uuid.UUID
