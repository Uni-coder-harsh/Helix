import uuid
from typing import Any

from services.governance.application.knowledge_service import KnowledgeService
from shared.domain.enums import Priority


class UrgencyEngine:
    """Computes urgency based on category, policies, and geographic critical assets."""

    def __init__(self, knowledge_service: KnowledgeService) -> None:
        self.knowledge_service = knowledge_service

    def calculate_urgency(
        self, category: str, latitude: float, longitude: float
    ) -> float:
        """Returns an urgency score from 0.0 to 1.0."""
        score = 0.4  # Base baseline urgency

        # Category multiplier
        cat_lower = category.lower()
        if "sanitat" in cat_lower or "garb" in cat_lower:
            score += 0.3
        elif "road" in cat_lower or "pothol" in cat_lower:
            score += 0.2

        # Geographic proximity boost (e.g., if near school/playground assets)
        ctx = self.knowledge_service.get_context_for_complaint(
            category, latitude, longitude
        )
        if ctx["nearby_assets"]:
            score += 0.2

        return min(score, 1.0)


class ImpactEngine:
    """Evaluates the affected population and expected societal outcomes."""

    def __init__(self, knowledge_service: KnowledgeService) -> None:
        self.knowledge_service = knowledge_service

    def estimate_impact(
        self, category: str, latitude: float, longitude: float
    ) -> dict[str, Any]:
        """Estimates affected population and expected outcome of resolving the issue."""
        ctx = self.knowledge_service.get_context_for_complaint(
            category, latitude, longitude
        )

        # Determine population estimation based on proximity to assets
        affected_pop = 150  # Default neighborhood base count
        if ctx["nearby_assets"]:
            # Near a public asset means higher traffic/impact
            affected_pop = 1200

        expected_outcome = (
            "Restores sanitary conditions, prevents public health hazards, "
            "and maintains cleanliness in ward public play areas."
            if "sanit" in category.lower() or "garb" in category.lower()
            else "Improves vehicle traffic throughput and eliminates pedestrian safety hazards."
        )

        return {
            "affected_population": affected_pop,
            "expected_outcome": expected_outcome,
            "impact_level": "HIGH" if affected_pop > 500 else "MEDIUM",
        }


class PriorityEngine:
    """Integrates urgency and impact metrics to determine final operational Priority."""

    @staticmethod
    def determine_priority(urgency_score: float, impact_level: str) -> Priority:
        if urgency_score >= 0.8 or (urgency_score >= 0.6 and impact_level == "HIGH"):
            return Priority.HIGH
        if urgency_score >= 0.4 or impact_level == "MEDIUM":
            return Priority.MEDIUM
        return Priority.LOW


class EvidenceAggregator:
    """Aggregates supporting evidence, active schemes, and nearby assets."""

    def __init__(self, knowledge_service: KnowledgeService) -> None:
        self.knowledge_service = knowledge_service

    def aggregate_evidence(
        self, category: str, latitude: float, longitude: float
    ) -> list[str]:
        ctx = self.knowledge_service.get_context_for_complaint(
            category, latitude, longitude
        )
        evidence_list = []
        for asset in ctx["nearby_assets"]:
            evidence_list.append(f"Municipal Asset Proximity: {asset['name']}")
        for scheme in ctx["schemes"]:
            evidence_list.append(f"Linked Municipal Scheme: {scheme['name']}")
        for policy in ctx["policies"]:
            evidence_list.append(f"Enforced Regulation: {policy['title']}")
        return evidence_list


class DecisionPolicyEngine:
    """Evaluates policy compliance, SLA boundaries, and confidence metrics."""

    def __init__(self, knowledge_service: KnowledgeService) -> None:
        self.knowledge_service = knowledge_service

    def evaluate_policy(self, category: str) -> dict[str, Any]:
        policies = self.knowledge_service.policies.find_policies_for_category(category)
        if not policies:
            return {
                "policy_aligned": False,
                "sla_hours": 48,
                "confidence": 0.5,
                "reasoning_chain": "No specific active policy matches this category. Defaulting to general SLA guidelines.",
            }

        # Select the primary policy
        policy = policies[0]
        sla_hours = 24 if policy["urgency_weight"] >= 0.8 else 48
        return {
            "policy_aligned": True,
            "sla_hours": sla_hours,
            "confidence": 0.95,
            "reasoning_chain": f"Aligned with Policy '{policy['title']}'. Evaluated rules: {policy['rules']}",
        }


class RecommendationBuilder:
    """Combines outputs from all decision engines to construct explainable recommendations."""

    def __init__(self, knowledge_service: KnowledgeService) -> None:
        self.knowledge_service = knowledge_service
        self.urgency_engine = UrgencyEngine(knowledge_service)
        self.impact_engine = ImpactEngine(knowledge_service)
        self.evidence_aggregator = EvidenceAggregator(knowledge_service)
        self.policy_engine = DecisionPolicyEngine(knowledge_service)

    def build_recommendation(
        self, issue_id: uuid.UUID, category: str, latitude: float, longitude: float
    ) -> dict[str, Any]:
        """Builds a complete explainable governance recommendation."""
        # 1. Compute urgency & impact
        urgency = self.urgency_engine.calculate_urgency(category, latitude, longitude)
        impact = self.impact_engine.estimate_impact(category, latitude, longitude)

        # 2. Determine Priority
        priority = PriorityEngine.determine_priority(urgency, impact["impact_level"])

        # 3. Aggregate Evidence & evaluate Policy SLA
        evidence = self.evidence_aggregator.aggregate_evidence(
            category, latitude, longitude
        )
        policy_eval = self.policy_engine.evaluate_policy(category)

        # 4. Resolve responsible department
        suggested_dept = (
            "Municipal Sanitation Department"
            if "sanit" in category.lower() or "garb" in category.lower()
            else "Public Works Department"
        )

        # 5. Formulate alternatives
        alternatives = [
            f"Dispatch private contract vendor for accelerated {category} remediation.",
            "Defer action to next routine scheduled ward maintenance cycle.",
        ]

        # 6. Formulate reasoning chain
        reasoning_chain = (
            f"1. Intake categorized issue as '{category}'.\n"
            f"2. Evaluated geo-spatial proximity; matched {len(evidence)} evidence points.\n"
            f"3. Determined urgency score: {urgency:.2f} and impact scale: {impact['impact_level']}.\n"
            f"4. Policy Evaluation: {policy_eval['reasoning_chain']}\n"
            f"5. Recommended dispatch to {suggested_dept} with SLA of {policy_eval['sla_hours']} hours."
        )

        return {
            "issue_id": issue_id,
            "priority": priority,
            "affected_population": impact["affected_population"],
            "estimated_impact": impact["impact_level"],
            "supporting_evidence": evidence,
            "confidence": policy_eval["confidence"],
            "reasoning_chain": reasoning_chain,
            "alternative_actions": alternatives,
            "suggested_department": suggested_dept,
            "expected_outcome": impact["expected_outcome"],
        }
