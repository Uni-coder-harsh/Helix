from enum import Enum

from pydantic import BaseModel, ConfigDict


class IssueStatus(str, Enum):
    """Workflow Engine issue statuses from ubiquitous language (HELIX-DOMAIN-001)."""

    DRAFT = "DRAFT"
    INTAKE = "INTAKE"
    TRIAGE = "TRIAGE"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class TaskStatus(str, Enum):
    """Task states within execution cycles."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class UserRole(str, Enum):
    """Security RBAC user roles."""

    CITIZEN = "CITIZEN"
    OFFICER = "OFFICER"
    ADMINISTRATOR = "ADMINISTRATOR"


class DomainModel(BaseModel):
    """Base domain model configured for Pydantic standard usage."""

    model_config = ConfigDict(from_attributes=True)
