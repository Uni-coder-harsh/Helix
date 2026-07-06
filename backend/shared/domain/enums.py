from enum import Enum


class Priority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CitizenStatus(Enum):
    ACTIVE = "ACTIVE"
    DEACTIVATED = "DEACTIVATED"


class OfficerStatus(Enum):
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"


class RepresentativeStatus(Enum):
    IN_OFFICE = "IN_OFFICE"
    TERM_ENDED = "TERM_ENDED"
    INACTIVE = "INACTIVE"


class IssueStatus(Enum):
    INGESTED = "INGESTED"
    TRIAGED = "TRIAGED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class TaskStatus(Enum):
    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"


class ProjectStatus(Enum):
    PLANNED = "PLANNED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


class DepartmentStatus(Enum):
    ACTIVE = "ACTIVE"
    MERGED = "MERGED"
    ARCHIVED = "ARCHIVED"


class SchemeStatus(Enum):
    PROPOSED = "PROPOSED"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"


class EvidenceStatus(Enum):
    EXTRACTED = "EXTRACTED"
    VERIFIED = "VERIFIED"
    ARCHIVED = "ARCHIVED"


class RecommendationStatus(Enum):
    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class OutcomeStatus(Enum):
    RECORDED = "RECORDED"
    VERIFIED = "VERIFIED"


class DecisionStatus(Enum):
    PROPOSED = "PROPOSED"
    SIGNED = "SIGNED"
    ARCHIVED = "ARCHIVED"
