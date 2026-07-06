from typing import Any

from shared.domain.knowledge.interfaces import (
    AdministrativeHierarchy,
    AssetStore,
    DepartmentStore,
    KnowledgeSearchInterface,
    PolicyStore,
    SchemeStore,
)


class KnowledgeService:
    """Application Service coordinating unified lookups across the Governance Knowledge base."""

    def __init__(
        self,
        policies: PolicyStore,
        schemes: SchemeStore,
        assets: AssetStore,
        hierarchy: AdministrativeHierarchy,
        departments: DepartmentStore,
        search: KnowledgeSearchInterface,
    ) -> None:
        self.policies = policies
        self.schemes = schemes
        self.assets = assets
        self.hierarchy = hierarchy
        self.departments = departments
        self.search = search

    def get_context_for_complaint(
        self, category: str, latitude: float, longitude: float
    ) -> dict[str, Any]:
        """Assembles policy rules, social schemes, and nearby assets to contextualize a complaint."""
        matched_policies = self.policies.find_policies_for_category(category)
        matched_schemes = self.schemes.find_matching_schemes({"category": category})
        nearby_assets = self.assets.find_nearby_assets(
            latitude, longitude, max_distance_km=2.0
        )

        return {
            "policies": matched_policies,
            "schemes": [{"id": s.id, "name": s.title} for s in matched_schemes],
            "nearby_assets": [
                {
                    "id": a.id,
                    "name": a.name,
                    "location": (a.location.latitude, a.location.longitude),
                }
                for a in nearby_assets
            ],
        }
