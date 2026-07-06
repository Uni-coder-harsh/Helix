import uuid
from typing import Any

from shared.domain.entities import Asset, Department, Scheme
from shared.domain.enums import DepartmentStatus, SchemeStatus
from shared.domain.knowledge.interfaces import (
    AdministrativeHierarchy,
    AssetStore,
    DepartmentStore,
    KnowledgeSearchInterface,
    PolicyStore,
    SchemeStore,
)
from shared.domain.value_objects import Location


class InMemoryPolicyStore(PolicyStore):
    """Static in-memory implementation of the PolicyStore interface."""

    def __init__(self) -> None:
        self._policies = {
            uuid.UUID("11111111-1111-1111-1111-111111111111"): {
                "id": uuid.UUID("11111111-1111-1111-1111-111111111111"),
                "title": "Sanitation Waste Management Regulation 2024",
                "category": "sanitation",
                "rules": "Garbage overflow must be cleared within 24 hours if situated near a public playground, school, or residential area; otherwise, the standard SLA is 48 hours.",
                "urgency_weight": 0.9,
                "impact_factor": 1.5,
            },
            uuid.UUID("22222222-2222-2222-2222-222222222222"): {
                "id": uuid.UUID("22222222-2222-2222-2222-222222222222"),
                "title": "Municipal Road Maintenance Policy 2023",
                "category": "roads",
                "rules": "Potholes on main arterial routes must be patched within 5 days; secondary or residential ward lanes hold a standard SLA of 10 days.",
                "urgency_weight": 0.6,
                "impact_factor": 1.2,
            },
        }

    def get_policy_by_id(self, policy_id: uuid.UUID) -> dict[str, Any] | None:
        return self._policies.get(policy_id)

    def find_policies_for_category(self, category: str) -> list[dict[str, Any]]:
        return [
            p
            for p in self._policies.values()
            if p["category"].lower() == category.lower()
        ]


class InMemorySchemeStore(SchemeStore):
    """Static in-memory implementation of the SchemeStore interface."""

    def __init__(self) -> None:
        # Construct Schemes using DDD constructor
        self._schemes = {
            uuid.UUID("33333333-3333-3333-3333-333333333333"): Scheme(
                id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
                department_id=uuid.UUID("99999999-9999-9999-9999-999999999999"),
                title="Swachh Ward Sanitation Subsidy",
                status=SchemeStatus.ACTIVE,
            ),
            uuid.UUID("44444444-4444-4444-4444-444444444444"): Scheme(
                id=uuid.UUID("44444444-4444-4444-4444-444444444444"),
                department_id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
                title="Arterial Road Rehabilitation Program",
                status=SchemeStatus.ACTIVE,
            ),
        }

    def get_scheme_by_id(self, scheme_id: uuid.UUID) -> Scheme | None:
        return self._schemes.get(scheme_id)

    def find_matching_schemes(self, criteria: dict[str, Any]) -> list[Scheme]:
        category = criteria.get("category", "").lower()
        if "sanit" in category or "garb" in category:
            return [self._schemes[uuid.UUID("33333333-3333-3333-3333-333333333333")]]
        if "road" in category or "pothole" in category:
            return [self._schemes[uuid.UUID("44444444-4444-4444-4444-444444444444")]]
        return []


class InMemoryAssetStore(AssetStore):
    """Static in-memory implementation of the AssetStore interface."""

    def __init__(self) -> None:
        self._assets = {
            uuid.UUID("55555555-5555-5555-5555-555555555555"): Asset(
                id=uuid.UUID("55555555-5555-5555-5555-555555555555"),
                department_id=uuid.UUID("99999999-9999-9999-9999-999999999999"),
                name="Ward 12 Playground Garbage Bin Terminal",
                location=Location(12.9716, 77.5946, "Ward 12 Playground Entrance"),
            ),
            uuid.UUID("66666666-6666-6666-6666-666666666666"): Asset(
                id=uuid.UUID("66666666-6666-6666-6666-666666666666"),
                department_id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
                name="Main Arterial Road Sector 4",
                location=Location(12.9750, 77.5990, "Richmond Road Overpass"),
            ),
        }

    def get_asset_by_id(self, asset_id: uuid.UUID) -> Asset | None:
        return self._assets.get(asset_id)

    def find_nearby_assets(
        self, latitude: float, longitude: float, max_distance_km: float
    ) -> list[Asset]:
        # Simple distance check for static mock ( Richmond Road vs Playground )
        nearby = []
        for asset in self._assets.values():
            lat_diff = abs(asset.location.latitude - latitude)
            lon_diff = abs(asset.location.longitude - longitude)
            # Rough approx: 1 deg = 111 km, so 0.01 deg is ~1.1 km
            if (lat_diff * 111 <= max_distance_km) and (
                lon_diff * 111 <= max_distance_km
            ):
                nearby.append(asset)
        return nearby


class InMemoryAdministrativeHierarchy(AdministrativeHierarchy):
    """Static in-memory implementation of constituency administrative metadata."""

    def __init__(self) -> None:
        self._constituencies = {
            uuid.UUID("77777777-7777-7777-7777-777777777777"): {
                "id": uuid.UUID("77777777-7777-7777-7777-777777777777"),
                "name": "Bangalore Central Constituency",
                "mp_name": "Shri Kumar Swamy",
                "total_wards": 15,
                "population": 450000,
            }
        }
        self._wards = {
            uuid.UUID("88888888-8888-8888-8888-888888888888"): {
                "id": uuid.UUID("88888888-8888-8888-8888-888888888888"),
                "name": "Ward 12 (Shivaji Nagar)",
                "constituency_id": uuid.UUID("77777777-7777-7777-7777-777777777777"),
                "corporator_name": "Smt. Latha R.",
                "demographics": {"under_18": 8000, "general": 25000},
            }
        }

    def get_constituency_metadata(
        self, constituency_id: uuid.UUID
    ) -> dict[str, Any] | None:
        return self._constituencies.get(constituency_id)

    def get_ward_details(self, ward_id: uuid.UUID) -> dict[str, Any] | None:
        return self._wards.get(ward_id)


class InMemoryDepartmentStore(DepartmentStore):
    """Static in-memory implementation of the DepartmentStore interface."""

    def __init__(self) -> None:
        self._departments = {
            uuid.UUID("99999999-9999-9999-9999-999999999999"): Department(
                id=uuid.UUID("99999999-9999-9999-9999-999999999999"),
                name="Municipal Sanitation Department",
                status=DepartmentStatus.ACTIVE,
            ),
            uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"): Department(
                id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
                name="Public Works Department",
                status=DepartmentStatus.ACTIVE,
            ),
        }

    def get_department_by_id(self, dept_id: uuid.UUID) -> Department | None:
        return self._departments.get(dept_id)

    def list_all_departments(self) -> list[Department]:
        return list(self._departments.values())


class InMemoryKnowledgeSearch(KnowledgeSearchInterface):
    """Unified simple search implementation."""

    def __init__(
        self,
        policies: PolicyStore,
        schemes: SchemeStore,
        assets: AssetStore,
    ) -> None:
        self.policies = policies
        self.schemes = schemes
        self.assets = assets

    def search_knowledge(
        self, query: str, _filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        query_lower = query.lower()
        results = []

        # Simple text containment lookup
        if "sanitat" in query_lower or "garb" in query_lower:
            results.append(
                {
                    "type": "policy",
                    "title": "Sanitation Waste Management Regulation 2024",
                    "relevance": 0.95,
                }
            )
            results.append(
                {
                    "type": "scheme",
                    "title": "Swachh Ward Sanitation Subsidy",
                    "relevance": 0.85,
                }
            )
        elif "road" in query_lower or "pothol" in query_lower:
            results.append(
                {
                    "type": "policy",
                    "title": "Municipal Road Maintenance Policy 2023",
                    "relevance": 0.95,
                }
            )
            results.append(
                {
                    "type": "scheme",
                    "title": "Arterial Road Rehabilitation Program",
                    "relevance": 0.85,
                }
            )

        return results
