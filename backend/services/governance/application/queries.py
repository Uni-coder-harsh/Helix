import uuid
from abc import ABC, abstractmethod
from typing import Any


class GovernanceQueryService(ABC):
    """CQRS read-model query service interface for the Governance Service."""

    @abstractmethod
    def list_pending_issues(self) -> list[dict[str, Any]]:
        """Retrieves a flat list of pending issues, including recommendation indicators."""
        pass

    @abstractmethod
    def get_recommendation_details(self, issue_id: uuid.UUID) -> dict[str, Any]:
        """Retrieves flat details of an AI recommendation for an issue."""
        pass

    @abstractmethod
    def get_dashboard_stats(self) -> dict[str, int]:
        """Retrieves aggregated statistics counts of issues grouped by state."""
        pass
