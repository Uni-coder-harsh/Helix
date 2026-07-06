import uuid
from abc import ABC, abstractmethod
from typing import Any

from shared.domain.entities import Asset, Department, Scheme


class PolicyStore(ABC):
    """Interface for loading and querying governance policies and rules."""

    @abstractmethod
    def get_policy_by_id(self, policy_id: uuid.UUID) -> dict[str, Any] | None:
        """Retrieves policy rules by its unique identifier."""
        pass

    @abstractmethod
    def find_policies_for_category(self, category: str) -> list[dict[str, Any]]:
        """Finds all policy guidelines relating to a specific category."""
        pass


class SchemeStore(ABC):
    """Interface for loading and querying social schemes and eligibility."""

    @abstractmethod
    def get_scheme_by_id(self, scheme_id: uuid.UUID) -> Scheme | None:
        """Retrieves scheme details by its unique identifier."""
        pass

    @abstractmethod
    def find_matching_schemes(self, criteria: dict[str, Any]) -> list[Scheme]:
        """Finds schemes matching specific eligibility criteria."""
        pass


class AssetStore(ABC):
    """Interface for querying municipal assets and facilities."""

    @abstractmethod
    def get_asset_by_id(self, asset_id: uuid.UUID) -> Asset | None:
        """Retrieves municipal asset details by ID."""
        pass

    @abstractmethod
    def find_nearby_assets(
        self, latitude: float, longitude: float, max_distance_km: float
    ) -> list[Asset]:
        """Finds municipal assets situated near geographical coordinates."""
        pass


class AdministrativeHierarchy(ABC):
    """Interface for querying administrative divisions (constituencies, wards)."""

    @abstractmethod
    def get_constituency_metadata(
        self, constituency_id: uuid.UUID
    ) -> dict[str, Any] | None:
        """Retrieves metadata properties for a given constituency."""
        pass

    @abstractmethod
    def get_ward_details(self, ward_id: uuid.UUID) -> dict[str, Any] | None:
        """Retrieves details of a municipal ward."""
        pass


class DepartmentStore(ABC):
    """Interface for querying departments and operational contacts."""

    @abstractmethod
    def get_department_by_id(self, dept_id: uuid.UUID) -> Department | None:
        """Retrieves department details by ID."""
        pass

    @abstractmethod
    def list_all_departments(self) -> list[Department]:
        """Lists all active operational departments."""
        pass


class KnowledgeSearchInterface(ABC):
    """Unified search lookup interface across all knowledge assets."""

    @abstractmethod
    def search_knowledge(
        self, query: str, filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Executes a structured search lookup across policy, scheme, and asset registries."""
        pass
