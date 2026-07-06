import uuid

from shared.domain.base import (
    AggregateRoot,
    BaseEntity,
    InvalidStateTransitionException,
    ValidationException,
)
from shared.domain.enums import (
    CitizenStatus,
    DecisionStatus,
    DepartmentStatus,
    EvidenceStatus,
    IssueStatus,
    OfficerStatus,
    OutcomeStatus,
    Priority,
    ProjectStatus,
    RecommendationStatus,
    SchemeStatus,
    TaskStatus,
)
from shared.domain.events import (
    CitizenDeactivatedEvent,
    DepartmentArchivedEvent,
    DepartmentMergedEvent,
    IssueClosedEvent,
    IssueInProgressEvent,
    IssueResolvedEvent,
    IssueTriagedEvent,
    ProjectActivatedEvent,
    ProjectApprovedEvent,
    ProjectCompletedEvent,
    RecommendationAcceptedEvent,
    RecommendationRejectedEvent,
    TaskAssignedEvent,
    TaskCompletedEvent,
    TaskCreatedEvent,
    TaskVerifiedEvent,
)
from shared.domain.value_objects import Attachment, Location


class Citizen(AggregateRoot[uuid.UUID]):
    def __init__(
        self,
        id: uuid.UUID,
        name: str,
        email: str,
        status: CitizenStatus = CitizenStatus.ACTIVE,
    ) -> None:
        super().__init__(id)
        if not name or not name.strip():
            raise ValidationException("Citizen name cannot be empty.")
        if not email or not email.strip() or "@" not in email:
            raise ValidationException(f"Invalid email: {email}")
        self._name = name
        self._email = email
        self._status = status

    @property
    def name(self) -> str:
        return self._name

    @property
    def email(self) -> str:
        return self._email

    @property
    def status(self) -> CitizenStatus:
        return self._status

    def deactivate(self, reason: str) -> None:
        if self._status == CitizenStatus.DEACTIVATED:
            return
        if not reason or not reason.strip():
            raise ValidationException("Reason for deactivation must be provided.")
        self._status = CitizenStatus.DEACTIVATED
        self.record_event(CitizenDeactivatedEvent(self.id, reason))


class Officer(BaseEntity[uuid.UUID]):
    def __init__(
        self,
        id: uuid.UUID,
        department_id: uuid.UUID,
        name: str,
        status: OfficerStatus = OfficerStatus.PROVISIONED,
    ) -> None:
        super().__init__(id)
        if not name or not name.strip():
            raise ValidationException("Officer name cannot be empty.")
        self._department_id = department_id
        self._name = name
        self._status = status

    @property
    def department_id(self) -> uuid.UUID:
        return self._department_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def status(self) -> OfficerStatus:
        return self._status

    def activate(self) -> None:
        if self._status == OfficerStatus.SUSPENDED:
            raise InvalidStateTransitionException(
                "Cannot activate a suspended officer."
            )
        self._status = OfficerStatus.ACTIVE

    def suspend(self) -> None:
        self._status = OfficerStatus.SUSPENDED


class Department(AggregateRoot[uuid.UUID]):
    def __init__(
        self,
        id: uuid.UUID,
        name: str,
        status: DepartmentStatus = DepartmentStatus.ACTIVE,
    ) -> None:
        super().__init__(id)
        if not name or not name.strip():
            raise ValidationException("Department name cannot be empty.")
        self._name = name
        self._status = status

    @property
    def name(self) -> str:
        return self._name

    @property
    def status(self) -> DepartmentStatus:
        return self._status

    def merge_into(self, target_department_id: uuid.UUID) -> None:
        if self._status == DepartmentStatus.ARCHIVED:
            raise InvalidStateTransitionException(
                "Cannot merge an archived department."
            )
        self._status = DepartmentStatus.MERGED
        self.record_event(DepartmentMergedEvent(self.id, target_department_id))

    def archive(self) -> None:
        if self._status == DepartmentStatus.ARCHIVED:
            return
        self._status = DepartmentStatus.ARCHIVED
        self.record_event(DepartmentArchivedEvent(self.id))


class Scheme(BaseEntity[uuid.UUID]):
    def __init__(
        self,
        id: uuid.UUID,
        department_id: uuid.UUID,
        title: str,
        status: SchemeStatus = SchemeStatus.PROPOSED,
    ) -> None:
        super().__init__(id)
        if not title or not title.strip():
            raise ValidationException("Scheme title cannot be empty.")
        self._department_id = department_id
        self._title = title
        self._status = status

    @property
    def department_id(self) -> uuid.UUID:
        return self._department_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def status(self) -> SchemeStatus:
        return self._status

    def activate(self) -> None:
        if self._status != SchemeStatus.PROPOSED:
            raise InvalidStateTransitionException(
                f"Scheme must be proposed before activation. Current: {self._status}"
            )
        self._status = SchemeStatus.ACTIVE

    def expire(self) -> None:
        if self._status != SchemeStatus.ACTIVE:
            raise InvalidStateTransitionException(
                f"Only active schemes can expire. Current: {self._status}"
            )
        self._status = SchemeStatus.EXPIRED


class Asset(BaseEntity[uuid.UUID]):
    def __init__(
        self,
        id: uuid.UUID,
        department_id: uuid.UUID,
        name: str,
        location: Location,
        status: str = "Active",
    ) -> None:
        super().__init__(id)
        if not name or not name.strip():
            raise ValidationException("Asset name cannot be empty.")
        self._department_id = department_id
        self._name = name
        self._location = location
        self._status = status

    @property
    def department_id(self) -> uuid.UUID:
        return self._department_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def location(self) -> Location:
        return self._location

    @property
    def status(self) -> str:
        return self._status

    def send_to_maintenance(self) -> None:
        self._status = "Maintenance"

    def decommission(self) -> None:
        self._status = "Decommissioned"


class Task(BaseEntity[uuid.UUID]):
    def __init__(
        self,
        id: uuid.UUID,
        issue_id: uuid.UUID,
        title: str,
        status: TaskStatus = TaskStatus.CREATED,
        officer_id: uuid.UUID | None = None,
        completion_notes: str | None = None,
        verified_by: uuid.UUID | None = None,
    ) -> None:
        super().__init__(id)
        if not title or not title.strip():
            raise ValidationException("Task title cannot be empty.")
        self._issue_id = issue_id
        self._title = title
        self._status = status
        self._officer_id = officer_id
        self._completion_notes = completion_notes
        self._verified_by = verified_by

    @property
    def issue_id(self) -> uuid.UUID:
        return self._issue_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def status(self) -> TaskStatus:
        return self._status

    @property
    def officer_id(self) -> uuid.UUID | None:
        return self._officer_id

    @property
    def completion_notes(self) -> str | None:
        return self._completion_notes

    @property
    def verified_by(self) -> uuid.UUID | None:
        return self._verified_by

    def assign(self, officer_id: uuid.UUID) -> None:
        if self._status != TaskStatus.CREATED:
            raise InvalidStateTransitionException(
                f"Task must be in CREATED state to assign. Current: {self._status}"
            )
        self._officer_id = officer_id
        self._status = TaskStatus.ASSIGNED

    def complete(self, completion_notes: str) -> None:
        if self._status != TaskStatus.ASSIGNED:
            raise InvalidStateTransitionException(
                "Task must be ASSIGNED before it can be completed. "
                f"Current: {self._status}"
            )
        if not completion_notes or not completion_notes.strip():
            raise ValidationException("Completion notes cannot be empty.")
        self._completion_notes = completion_notes
        self._status = TaskStatus.COMPLETED

    def verify(self, officer_id: uuid.UUID) -> None:
        if self._status != TaskStatus.COMPLETED:
            raise InvalidStateTransitionException(
                f"Task must be COMPLETED before verification. Current: {self._status}"
            )
        self._verified_by = officer_id
        self._status = TaskStatus.VERIFIED


class Issue(AggregateRoot[uuid.UUID]):
    def __init__(
        self,
        id: uuid.UUID,
        citizen_id: uuid.UUID,
        title: str,
        description: str,
        category: str,
        location: Location,
        status: IssueStatus = IssueStatus.INGESTED,
        priority: Priority | None = None,
        department_id: uuid.UUID | None = None,
        tasks: list[Task] | None = None,
        attachments: list[Attachment] | None = None,
    ) -> None:
        super().__init__(id)
        if not title or not title.strip():
            raise ValidationException("Issue title cannot be empty.")
        if not description or not description.strip():
            raise ValidationException("Issue description cannot be empty.")
        if not category or not category.strip():
            raise ValidationException("Issue category cannot be empty.")

        self._citizen_id = citizen_id
        self._title = title
        self._description = description
        self._category = category
        self._location = location
        self._status = status
        self._priority = priority
        self._department_id = department_id
        self._tasks: list[Task] = tasks or []
        self._attachments: list[Attachment] = attachments or []

    @property
    def citizen_id(self) -> uuid.UUID:
        return self._citizen_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def category(self) -> str:
        return self._category

    @property
    def location(self) -> Location:
        return self._location

    @property
    def status(self) -> IssueStatus:
        return self._status

    @property
    def priority(self) -> Priority | None:
        return self._priority

    @property
    def department_id(self) -> uuid.UUID | None:
        return self._department_id

    @property
    def tasks(self) -> list[Task]:
        return list(self._tasks)

    @property
    def attachments(self) -> list[Attachment]:
        return list(self._attachments)

    def triage(self, department_id: uuid.UUID, priority: Priority) -> None:
        if self._status != IssueStatus.INGESTED:
            raise InvalidStateTransitionException(
                f"Issue must be INGESTED to be triaged. Current: {self._status}"
            )
        self._department_id = department_id
        self._priority = priority
        self._status = IssueStatus.TRIAGED
        self.record_event(IssueTriagedEvent(self.id, department_id, priority))

    def add_task(self, task_id: uuid.UUID, title: str) -> Task:
        if self._status not in (IssueStatus.TRIAGED, IssueStatus.IN_PROGRESS):
            raise InvalidStateTransitionException(
                f"Cannot add tasks in current state: {self._status}"
            )
        if not self.department_id:
            raise ValidationException(
                "Issue must have a department assigned before tasks can be created."
            )

        task = Task(id=task_id, issue_id=self.id, title=title)
        self._tasks.append(task)

        if self._status == IssueStatus.TRIAGED:
            self._status = IssueStatus.IN_PROGRESS
            self.record_event(IssueInProgressEvent(self.id))

        self.record_event(TaskCreatedEvent(task.id, self.id, title, self.department_id))
        return task

    def assign_task(self, task_id: uuid.UUID, officer_id: uuid.UUID) -> None:
        task = next((t for t in self._tasks if t.id == task_id), None)
        if not task:
            raise ValidationException(
                f"Task with ID {task_id} not found in this Issue."
            )
        task.assign(officer_id)
        self.record_event(TaskAssignedEvent(task_id, officer_id))

    def complete_task(self, task_id: uuid.UUID, completion_notes: str) -> None:
        task = next((t for t in self._tasks if t.id == task_id), None)
        if not task:
            raise ValidationException(
                f"Task with ID {task_id} not found in this Issue."
            )
        task.complete(completion_notes)
        self.record_event(TaskCompletedEvent(task_id, completion_notes))

    def verify_task(self, task_id: uuid.UUID, officer_id: uuid.UUID) -> None:
        task = next((t for t in self._tasks if t.id == task_id), None)
        if not task:
            raise ValidationException(
                f"Task with ID {task_id} not found in this Issue."
            )
        task.verify(officer_id)
        self.record_event(TaskVerifiedEvent(task_id, officer_id))

    def resolve(self, resolution_notes: str) -> None:
        if self._status != IssueStatus.IN_PROGRESS:
            raise InvalidStateTransitionException(
                f"Issue must be IN_PROGRESS to resolve. Current: {self._status}"
            )
        if not resolution_notes or not resolution_notes.strip():
            raise ValidationException("Resolution notes cannot be empty.")

        # Invariant: All tasks must be completed and verified
        if not self._tasks:
            raise ValidationException("Cannot resolve an issue that has no tasks.")
        for task in self._tasks:
            if task.status != TaskStatus.VERIFIED:
                raise ValidationException(
                    "All tasks must be verified before resolving the issue. "
                    f"Task {task.id} is {task.status.value}."
                )

        self._status = IssueStatus.RESOLVED
        self.record_event(IssueResolvedEvent(self.id, resolution_notes))

    def close(self, feedback_score: int | None = None) -> None:
        if self._status != IssueStatus.RESOLVED:
            raise InvalidStateTransitionException(
                f"Issue must be RESOLVED to close. Current: {self._status}"
            )
        if feedback_score is not None and not (1 <= feedback_score <= 5):
            raise ValidationException(
                f"Feedback score must be between 1 and 5. Got: {feedback_score}"
            )

        self._status = IssueStatus.CLOSED
        self.record_event(IssueClosedEvent(self.id, feedback_score))


class Project(AggregateRoot[uuid.UUID]):
    def __init__(
        self,
        id: uuid.UUID,
        representative_id: uuid.UUID,
        title: str,
        status: ProjectStatus = ProjectStatus.PLANNED,
        task_ids: list[uuid.UUID] | None = None,
        asset_ids: list[uuid.UUID] | None = None,
    ) -> None:
        super().__init__(id)
        if not title or not title.strip():
            raise ValidationException("Project title cannot be empty.")
        self._representative_id = representative_id
        self._title = title
        self._status = status
        self._task_ids: list[uuid.UUID] = task_ids or []
        self._asset_ids: list[uuid.UUID] = asset_ids or []

    @property
    def representative_id(self) -> uuid.UUID:
        return self._representative_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def status(self) -> ProjectStatus:
        return self._status

    @property
    def task_ids(self) -> list[uuid.UUID]:
        return list(self._task_ids)

    @property
    def asset_ids(self) -> list[uuid.UUID]:
        return list(self._asset_ids)

    def approve(self, officer_id: uuid.UUID) -> None:
        if self._status != ProjectStatus.PLANNED:
            raise InvalidStateTransitionException(
                f"Only PLANNED projects can be approved. Current: {self._status}"
            )
        self._status = ProjectStatus.APPROVED
        self.record_event(ProjectApprovedEvent(self.id, officer_id))

    def activate(self) -> None:
        if self._status != ProjectStatus.APPROVED:
            raise InvalidStateTransitionException(
                f"Only APPROVED projects can be activated. Current: {self._status}"
            )
        self._status = ProjectStatus.ACTIVE
        self.record_event(ProjectActivatedEvent(self.id))

    def complete(self, completion_summary: str) -> None:
        if self._status != ProjectStatus.ACTIVE:
            raise InvalidStateTransitionException(
                f"Only ACTIVE projects can be completed. Current: {self._status}"
            )
        if not completion_summary or not completion_summary.strip():
            raise ValidationException("Completion summary cannot be empty.")
        self._status = ProjectStatus.COMPLETED
        self.record_event(ProjectCompletedEvent(self.id, completion_summary))


class Evidence(BaseEntity[uuid.UUID]):
    def __init__(
        self,
        id: uuid.UUID,
        source_type: str,
        source_id: uuid.UUID,
        content: str,
        status: EvidenceStatus = EvidenceStatus.EXTRACTED,
    ) -> None:
        super().__init__(id)
        if not source_type or not source_type.strip():
            raise ValidationException("Evidence source type cannot be empty.")
        if not content or not content.strip():
            raise ValidationException("Evidence content cannot be empty.")
        self._source_type = source_type
        self._source_id = source_id
        self._content = content
        self._status = status

    @property
    def source_type(self) -> str:
        return self._source_type

    @property
    def source_id(self) -> uuid.UUID:
        return self._source_id

    @property
    def content(self) -> str:
        return self._content

    @property
    def status(self) -> EvidenceStatus:
        return self._status

    def verify(self) -> None:
        if self._status != EvidenceStatus.EXTRACTED:
            raise InvalidStateTransitionException(
                "Evidence can only be verified from EXTRACTED state. "
                f"Current: {self._status}"
            )
        self._status = EvidenceStatus.VERIFIED

    def archive(self) -> None:
        self._status = EvidenceStatus.ARCHIVED


class Recommendation(AggregateRoot[uuid.UUID]):
    def __init__(
        self,
        id: uuid.UUID,
        issue_id: uuid.UUID,
        evidence_ids: list[uuid.UUID],
        content: str,
        status: RecommendationStatus = RecommendationStatus.PROPOSED,
    ) -> None:
        super().__init__(id)
        if not evidence_ids:
            raise ValidationException(
                "Recommendation must be backed by at least one evidence."
            )
        if not content or not content.strip():
            raise ValidationException("Recommendation content cannot be empty.")
        self._issue_id = issue_id
        self._evidence_ids = list(evidence_ids)
        self._content = content
        self._status = status

    @property
    def issue_id(self) -> uuid.UUID:
        return self._issue_id

    @property
    def evidence_ids(self) -> list[uuid.UUID]:
        return list(self._evidence_ids)

    @property
    def content(self) -> str:
        return self._content

    @property
    def status(self) -> RecommendationStatus:
        return self._status

    def accept(self, decision_id: uuid.UUID) -> None:
        if self._status != RecommendationStatus.PROPOSED:
            raise InvalidStateTransitionException(
                "Recommendation can only be accepted if it is PROPOSED. "
                f"Current: {self._status}"
            )
        self._status = RecommendationStatus.ACCEPTED
        self.record_event(RecommendationAcceptedEvent(self.id, decision_id))

    def reject(self, reason: str) -> None:
        if self._status != RecommendationStatus.PROPOSED:
            raise InvalidStateTransitionException(
                "Recommendation can only be rejected if it is PROPOSED. "
                f"Current: {self._status}"
            )
        if not reason or not reason.strip():
            raise ValidationException("Reason for rejection must be provided.")
        self._status = RecommendationStatus.REJECTED
        self.record_event(RecommendationRejectedEvent(self.id, reason))


class Decision(BaseEntity[uuid.UUID]):
    def __init__(
        self,
        id: uuid.UUID,
        authorized_by: uuid.UUID,
        target_id: uuid.UUID,
        status: DecisionStatus = DecisionStatus.PROPOSED,
    ) -> None:
        super().__init__(id)
        self._authorized_by = authorized_by
        self._target_id = target_id
        self._status = status

    @property
    def authorized_by(self) -> uuid.UUID:
        return self._authorized_by

    @property
    def target_id(self) -> uuid.UUID:
        return self._target_id

    @property
    def status(self) -> DecisionStatus:
        return self._status

    def sign(self) -> None:
        if self._status != DecisionStatus.PROPOSED:
            raise InvalidStateTransitionException(
                "Decision can only be signed from PROPOSED state. "
                f"Current: {self._status}"
            )
        self._status = DecisionStatus.SIGNED

    def archive(self) -> None:
        self._status = DecisionStatus.ARCHIVED


class Outcome(BaseEntity[uuid.UUID]):
    def __init__(
        self,
        id: uuid.UUID,
        target_id: uuid.UUID,
        metric_name: str,
        score: float,
        status: OutcomeStatus = OutcomeStatus.RECORDED,
        verified_by: uuid.UUID | None = None,
    ) -> None:
        super().__init__(id)
        if not metric_name or not metric_name.strip():
            raise ValidationException("Outcome metric name cannot be empty.")
        if not (0.0 <= score <= 100.0):
            raise ValidationException(
                f"Outcome score must be between 0.0 and 100.0. Got: {score}"
            )
        self._target_id = target_id
        self._metric_name = metric_name
        self._score = score
        self._status = status
        self._verified_by = verified_by

    @property
    def target_id(self) -> uuid.UUID:
        return self._target_id

    @property
    def metric_name(self) -> str:
        return self._metric_name

    @property
    def score(self) -> float:
        return self._score

    @property
    def status(self) -> OutcomeStatus:
        return self._status

    @property
    def verified_by(self) -> uuid.UUID | None:
        return self._verified_by

    def verify(self, officer_id: uuid.UUID) -> None:
        if self._status != OutcomeStatus.RECORDED:
            raise InvalidStateTransitionException(
                f"Outcome must be in RECORDED state to verify. Current: {self._status}"
            )
        self._verified_by = officer_id
        self._status = OutcomeStatus.VERIFIED
