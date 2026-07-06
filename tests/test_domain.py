import uuid

import pytest

from shared.contracts.commands import (
    RegisterCitizenCommand,
)
from shared.contracts.queries import (
    GetIssueQuery,
)
from shared.domain.base import (
    BaseEntity,
    DomainEvent,
    InvalidStateTransitionException,
    ValidationException,
    ValueObject,
)
from shared.domain.entities import (
    Asset,
    Citizen,
    Department,
    Evidence,
    Issue,
    Officer,
    Outcome,
    Project,
    Recommendation,
    Scheme,
)
from shared.domain.enums import (
    CitizenStatus,
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
    TaskCreatedEvent,
)
from shared.domain.validation import (
    validate_email,
    validate_non_empty_string,
    validate_range,
)
from shared.domain.value_objects import Attachment, Location

# ==========================================
# 1. Base Class Tests
# ==========================================


class SampleEntity(BaseEntity[uuid.UUID]):
    pass


class SampleValueObject(ValueObject):
    def __init__(self, val1: str, val2: int) -> None:
        self.val1 = val1
        self.val2 = val2


class SampleEvent(DomainEvent):
    pass


def test_base_entity_equality() -> None:
    id1 = uuid.uuid4()
    id2 = uuid.uuid4()
    e1 = SampleEntity(id1)
    e2 = SampleEntity(id1)
    e3 = SampleEntity(id2)

    assert e1 == e2
    assert e1 != e3
    assert hash(e1) == hash(e2)
    assert hash(e1) != hash(e3)


def test_value_object_equality() -> None:
    vo1 = SampleValueObject("hello", 123)
    vo2 = SampleValueObject("hello", 123)
    vo3 = SampleValueObject("world", 123)
    vo4 = SampleValueObject("hello", 456)

    assert vo1 == vo2
    assert vo1 != vo3
    assert vo1 != vo4
    assert hash(vo1) == hash(vo2)
    assert hash(vo1) != hash(vo3)


def test_domain_event_generation() -> None:
    evt = SampleEvent()
    assert evt.event_id is not None
    assert evt.occurred_on is not None

    evt2 = SampleEvent(event_id=evt.event_id)
    assert evt == evt2


# ==========================================
# 2. Validation Helper Tests
# ==========================================


def test_validate_non_empty_string() -> None:
    assert validate_non_empty_string("  test  ", "field") == "test"
    with pytest.raises(ValidationException):
        validate_non_empty_string("", "field")
    with pytest.raises(ValidationException):
        validate_non_empty_string("   ", "field")
    with pytest.raises(ValidationException):
        validate_non_empty_string(123, "field")  # type: ignore


def test_validate_email() -> None:
    assert validate_email("harsh@gemini.com") == "harsh@gemini.com"
    with pytest.raises(ValidationException):
        validate_email("invalid-email")
    with pytest.raises(ValidationException):
        validate_email("harsh@")
    with pytest.raises(ValidationException):
        validate_email("@gemini.com")


def test_validate_range() -> None:
    assert validate_range(50.0, "score", 0.0, 100.0) == 50.0
    with pytest.raises(ValidationException):
        validate_range(-1.0, "score", 0.0, 100.0)
    with pytest.raises(ValidationException):
        validate_range(100.1, "score", 0.0, 100.0)


# ==========================================
# 3. Value Object Tests (Location, Attachment)
# ==========================================


def test_location_validation() -> None:
    # Valid
    loc = Location(latitude=28.6139, longitude=77.2090, formatted_address="New Delhi")
    assert loc.latitude == 28.6139

    # Invalid coordinates
    with pytest.raises(ValidationException):
        Location(latitude=91.0, longitude=77.2090, formatted_address="New Delhi")
    with pytest.raises(ValidationException):
        Location(latitude=28.6139, longitude=-181.0, formatted_address="New Delhi")

    # Empty Address
    with pytest.raises(ValidationException):
        Location(latitude=28.6139, longitude=77.2090, formatted_address=" ")


def test_attachment_validation() -> None:
    # Valid
    att = Attachment(
        file_url="http://storage/img.png",
        file_name="img.png",
        mime_type="image/png",
        file_size_bytes=1024,
        checksum="abcd1234",
    )
    assert att.file_name == "img.png"

    # Invalid size
    with pytest.raises(ValidationException):
        Attachment(
            file_url="http://storage/img.png",
            file_name="img.png",
            mime_type="image/png",
            file_size_bytes=-10,
            checksum="abcd1234",
        )
    # Empty checksum
    with pytest.raises(ValidationException):
        Attachment(
            file_url="http://storage/img.png",
            file_name="img.png",
            mime_type="image/png",
            file_size_bytes=1024,
            checksum="",
        )


# ==========================================
# 4. Human Domain Entities Tests (Citizen, Officer)
# ==========================================


def test_citizen_lifecycle() -> None:
    citizen_id = uuid.uuid4()
    citizen = Citizen(id=citizen_id, name="Harsh", email="harsh@gemini.com")
    assert citizen.name == "Harsh"
    assert citizen.status == CitizenStatus.ACTIVE

    citizen.deactivate(reason="Requested account deletion")
    assert citizen.status == CitizenStatus.DEACTIVATED

    # Check domain event
    events = citizen.domain_events
    assert len(events) == 1
    assert isinstance(events[0], CitizenDeactivatedEvent)
    assert events[0].citizen_id == citizen_id
    assert events[0].reason == "Requested account deletion"


def test_officer_lifecycle() -> None:
    officer_id = uuid.uuid4()
    dept_id = uuid.uuid4()
    officer = Officer(id=officer_id, department_id=dept_id, name="Officer Dave")
    assert officer.status == OfficerStatus.PROVISIONED

    officer.activate()
    assert officer.status == OfficerStatus.ACTIVE

    officer.suspend()
    assert officer.status == OfficerStatus.SUSPENDED

    with pytest.raises(InvalidStateTransitionException):
        officer.activate()  # Cannot activate suspended directly


# ==========================================
# 5. Governance Domain Entities Tests (Dept, Scheme, Asset)
# ==========================================


def test_department_lifecycle() -> None:
    dept_id = uuid.uuid4()
    dept = Department(id=dept_id, name="Sanitation")
    assert dept.status == DepartmentStatus.ACTIVE

    target_id = uuid.uuid4()
    dept.merge_into(target_id)
    assert dept.status == DepartmentStatus.MERGED
    assert isinstance(dept.domain_events[0], DepartmentMergedEvent)

    dept.clear_domain_events()
    dept.archive()
    assert dept.status == DepartmentStatus.ARCHIVED
    assert isinstance(dept.domain_events[0], DepartmentArchivedEvent)


def test_scheme_lifecycle() -> None:
    scheme_id = uuid.uuid4()
    dept_id = uuid.uuid4()
    scheme = Scheme(id=scheme_id, department_id=dept_id, title="Clean Water Scheme")
    assert scheme.status == SchemeStatus.PROPOSED

    scheme.activate()
    assert scheme.status == SchemeStatus.ACTIVE

    scheme.expire()
    assert scheme.status == SchemeStatus.EXPIRED

    # Invalid transition
    scheme_proposed = Scheme(id=scheme_id, department_id=dept_id, title="Water")
    with pytest.raises(InvalidStateTransitionException):
        scheme_proposed.expire()


def test_asset_lifecycle() -> None:
    asset_id = uuid.uuid4()
    dept_id = uuid.uuid4()
    loc = Location(latitude=12.0, longitude=12.0, formatted_address="Panchayat Ward 3")
    asset = Asset(
        id=asset_id, department_id=dept_id, name="Pumping Station #3", location=loc
    )
    assert asset.status == "Active"

    asset.send_to_maintenance()
    assert asset.status == "Maintenance"

    asset.decommission()
    assert asset.status == "Decommissioned"


# ==========================================
# 6. Operational Domain Entities Tests (Issue, Task)
# ==========================================


def test_issue_state_machine() -> None:
    citizen_id = uuid.uuid4()
    issue_id = uuid.uuid4()
    dept_id = uuid.uuid4()
    loc = Location(latitude=10.0, longitude=20.0, formatted_address="Street Road")

    # Ingestion
    issue = Issue(
        id=issue_id,
        citizen_id=citizen_id,
        title="Water leak",
        description="Major leak on crossroad 4",
        category="Infrastructure",
        location=loc,
    )
    assert issue.status == IssueStatus.INGESTED

    # Try resolving/closing from Ingested (Invalid)
    with pytest.raises(InvalidStateTransitionException):
        issue.resolve("Done")
    with pytest.raises(InvalidStateTransitionException):
        issue.close()

    # Triage
    issue.triage(department_id=dept_id, priority=Priority.HIGH)
    assert issue.status == IssueStatus.TRIAGED
    assert issue.priority == Priority.HIGH
    assert issue.department_id == dept_id
    assert any(isinstance(e, IssueTriagedEvent) for e in issue.domain_events)

    # Add Task (Transitions to In-Progress)
    task1_id = uuid.uuid4()
    task1 = issue.add_task(task1_id, "Weld pipe crack")
    assert issue.status == IssueStatus.IN_PROGRESS
    assert len(issue.tasks) == 1
    assert task1.status == TaskStatus.CREATED
    assert any(isinstance(e, IssueInProgressEvent) for e in issue.domain_events)
    assert any(isinstance(e, TaskCreatedEvent) for e in issue.domain_events)

    # Assign Task
    officer_id = uuid.uuid4()
    issue.assign_task(task1_id, officer_id)
    assert task1.status == TaskStatus.ASSIGNED
    assert task1.officer_id == officer_id

    # Complete Task
    issue.complete_task(task1_id, "Pipe welded successfully")
    assert task1.status == TaskStatus.COMPLETED
    assert task1.completion_notes == "Pipe welded successfully"

    # Try resolving before verification (Invalid)
    with pytest.raises(ValidationException):
        issue.resolve("Resolution")

    # Verify Task
    issue.verify_task(task1_id, officer_id)
    assert task1.status == TaskStatus.VERIFIED

    # Resolve Issue
    issue.resolve("Resolution notes here")
    assert issue.status == IssueStatus.RESOLVED
    assert any(isinstance(e, IssueResolvedEvent) for e in issue.domain_events)

    # Close Issue
    issue.close(feedback_score=5)
    assert issue.status == IssueStatus.CLOSED
    assert any(isinstance(e, IssueClosedEvent) for e in issue.domain_events)


def test_project_lifecycle() -> None:
    project_id = uuid.uuid4()
    rep_id = uuid.uuid4()
    task_id = uuid.uuid4()
    asset_id = uuid.uuid4()

    project = Project(
        id=project_id,
        representative_id=rep_id,
        title="Sanitation Uplift",
        task_ids=[task_id],
        asset_ids=[asset_id],
    )
    assert project.status == ProjectStatus.PLANNED

    # Try activating before approval
    with pytest.raises(InvalidStateTransitionException):
        project.activate()

    officer_id = uuid.uuid4()
    project.approve(officer_id)
    assert project.status == ProjectStatus.APPROVED
    assert any(isinstance(e, ProjectApprovedEvent) for e in project.domain_events)

    project.activate()
    assert project.status == ProjectStatus.ACTIVE
    assert any(isinstance(e, ProjectActivatedEvent) for e in project.domain_events)

    project.complete("Completed successfully")
    assert project.status == ProjectStatus.COMPLETED
    assert any(isinstance(e, ProjectCompletedEvent) for e in project.domain_events)


def test_evidence_and_recommendation() -> None:
    evidence_id = uuid.uuid4()
    issue_id = uuid.uuid4()

    evidence = Evidence(
        id=evidence_id,
        source_type="PolicyDocument",
        source_id=uuid.uuid4(),
        content="Water directive section 4",
    )
    assert evidence.status == EvidenceStatus.EXTRACTED
    evidence.verify()
    assert evidence.status == EvidenceStatus.VERIFIED

    rec_id = uuid.uuid4()
    rec = Recommendation(
        id=rec_id,
        issue_id=issue_id,
        evidence_ids=[evidence_id],
        content="Deploy secondary valve",
    )
    assert rec.status == RecommendationStatus.PROPOSED

    dec_id = uuid.uuid4()
    rec.accept(dec_id)
    assert rec.status == RecommendationStatus.ACCEPTED


def test_outcome_lifecycle() -> None:
    outcome_id = uuid.uuid4()
    target_id = uuid.uuid4()

    outcome = Outcome(
        id=outcome_id, target_id=target_id, metric_name="CleanlinessIndex", score=92.5
    )
    assert outcome.status == OutcomeStatus.RECORDED

    officer_id = uuid.uuid4()
    outcome.verify(officer_id)
    assert outcome.status == OutcomeStatus.VERIFIED
    assert outcome.verified_by == officer_id


# ==========================================
# 7. CQRS Commands and Queries Instantiation
# ==========================================


def test_commands_queries_instantiation() -> None:
    c_id = uuid.uuid4()
    cmd = RegisterCitizenCommand(citizen_id=c_id, name="A", email="a@b.com")
    assert cmd.citizen_id == c_id
    assert cmd.command_id is not None
    assert cmd.timestamp is not None

    issue_id = uuid.uuid4()
    q = GetIssueQuery(issue_id=issue_id)
    assert q.issue_id == issue_id
    assert q.query_id is not None
