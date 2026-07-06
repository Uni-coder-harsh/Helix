import uuid
from abc import ABC, abstractmethod

from shared.domain.entities import Issue


class IssueRepository(ABC):
    """Domain interface for Issue persistence."""

    @abstractmethod
    def save(self, issue: Issue) -> None:
        """Persists the issue aggregate state."""
        pass

    @abstractmethod
    def get_by_id(self, issue_id: uuid.UUID) -> Issue | None:
        """Retrieves the issue aggregate by its unique identifier."""
        pass
