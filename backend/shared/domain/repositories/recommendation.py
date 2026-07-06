import uuid
from abc import ABC, abstractmethod

from shared.domain.entities import Recommendation


class RecommendationRepository(ABC):
    """Domain interface for AI Recommendation persistence."""

    @abstractmethod
    def save(
        self,
        recommendation: Recommendation,
        suggested_category: str | None = None,
        suggested_department: str | None = None,
        confidence_score: float | None = None,
    ) -> None:
        """Persists the recommendation aggregate state, along with metadata details."""
        pass

    @abstractmethod
    def get_by_id(self, recommendation_id: uuid.UUID) -> Recommendation | None:
        """Retrieves the recommendation aggregate by its unique identifier."""
        pass

    @abstractmethod
    def get_by_issue_id(self, issue_id: uuid.UUID) -> Recommendation | None:
        """Retrieves the recommendation aggregate associated with a specific issue."""
        pass
