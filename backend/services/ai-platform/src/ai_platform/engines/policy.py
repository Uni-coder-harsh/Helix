from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PolicyDocument:
    policy_id: str
    title: str
    content: str
    categories: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


class PolicyRetrievalInterface(ABC):
    @abstractmethod
    async def retrieve_policies(
        self, context: dict[str, Any], query: str | None = None
    ) -> list[PolicyDocument]:
        """Retrieve relevant PolicyDocuments based on governance context and search query."""
        pass


class InMemoryPolicyRegistry(PolicyRetrievalInterface):
    """
    In-memory policy database preloaded with generic, scalable policies
    covering municipal and civic service level agreements (SLAs).
    """

    def __init__(self) -> None:
        self.policies: list[PolicyDocument] = []
        self._bootstrap_policies()

    def add_policy(self, policy: PolicyDocument) -> None:
        self.policies.append(policy)

    async def retrieve_policies(
        self, context: dict[str, Any], query: str | None = None
    ) -> list[PolicyDocument]:
        category_filter = context.get("category")
        ward_filter = context.get("ward")

        matches = []
        for policy in self.policies:
            # Filter by category if provided
            if category_filter and category_filter not in policy.categories:
                continue

            # Filter by ward eligibility if specified in policy metadata
            policy_wards = policy.metadata.get("eligible_wards", [])
            if ward_filter and policy_wards and (ward_filter not in policy_wards):
                continue

            # Direct text search match if query string is present
            if query:
                q = query.lower()
                if (q not in policy.title.lower()) and (
                    q not in policy.content.lower()
                ):
                    continue

            matches.append(policy)

        return matches

    def _bootstrap_policies(self) -> None:
        self.add_policy(
            PolicyDocument(
                policy_id="POL-SAN-001",
                title="Municipal Sanitation & Waste Removal Regulations",
                content="All waste disposal complaints must be addressed within 48 hours of filing. Commercial sectors are subject to daily pickup, while residential sectors receive pickup thrice weekly. Public garbage bin overflow reports require emergency dispatch within 12 hours.",
                categories=["sanitation", "civic_amenities"],
                metadata={
                    "eligible_wards": ["Ward 5", "Ward 12", "Ward 15"],
                    "sla_hours": 48,
                },
            )
        )

        self.add_policy(
            PolicyDocument(
                policy_id="POL-RD-002",
                title="Road Maintenance & Pothole Repair Standard Operating Procedure",
                content="Potholes on primary highways must be repaired within 24 hours of confirmation. Potholes on residential roads must be repaired within 5 business days. Photographic evidence and latitude/longitude coordinates must be submitted alongside work verification orders.",
                categories=["infrastructure", "roads"],
                metadata={
                    "eligible_wards": [],
                    "sla_hours": 120,
                },  # Empty wards list = globally eligible
            )
        )

        self.add_policy(
            PolicyDocument(
                policy_id="POL-SEC-003",
                title="Streetlight Fault and Public Safety Maintenance Directives",
                content="Dark area and broken streetlight complaints must be resolved in 72 hours. High-crime zones (Category A sectors) receive priority dispatch within 24 hours. A valid complaint must contain the pole identity number or nearest street address.",
                categories=["public_safety", "electricity"],
                metadata={"eligible_wards": ["Ward 5", "Ward 9"], "sla_hours": 72},
            )
        )
