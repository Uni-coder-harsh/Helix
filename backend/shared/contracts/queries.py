import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, kw_only=True)
class BaseQuery:
    query_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, kw_only=True)
class GetCitizenQuery(BaseQuery):
    citizen_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class GetIssueQuery(BaseQuery):
    issue_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class ListIssuesQuery(BaseQuery):
    citizen_id: uuid.UUID | None = None
    department_id: uuid.UUID | None = None
    status: str | None = None
    limit: int = 10
    offset: int = 0


@dataclass(frozen=True, kw_only=True)
class GetTaskQuery(BaseQuery):
    task_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class ListTasksForIssueQuery(BaseQuery):
    issue_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class GetProjectQuery(BaseQuery):
    project_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class GetSchemeQuery(BaseQuery):
    scheme_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class GetDepartmentQuery(BaseQuery):
    department_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class GetRecommendationQuery(BaseQuery):
    recommendation_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class GetOutcomeQuery(BaseQuery):
    outcome_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class ListOutcomesForTargetQuery(BaseQuery):
    target_id: uuid.UUID
