import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from ai_platform.engines.evidence import (
    EvidenceEngine,
    EvidenceFile,
)
from ai_platform.engines.policy import PolicyRetrievalInterface
from ai_platform.engines.reasoning import ReasoningEngine, ReasoningOutcome


@dataclass
class Recommendation:
    recommendation_id: str
    issue_id: str
    suggested_action: str
    priority_score: float
    reasoning: ReasoningOutcome
    evidence_status: str
    confidence_score: float
    policies_consulted: list[str]
    safety_passed: bool
    grounding_score: float
    hallucination_detected: bool
    metadata: dict[str, Any]


class RecommendationEngine(ABC):
    @abstractmethod
    async def generate_recommendation(
        self,
        issue_id: str,
        issue_content: str,
        metadata: dict[str, Any],
        files: list[EvidenceFile],
    ) -> Recommendation:
        """Generate a complete advisory recommendation including policy reasoning and safety audit."""
        pass


class OrchestratedRecommendationEngine(RecommendationEngine):
    """
    Core Recommendation Engine.
    Orchestrates policy retrieval, evidence verification, multi-step logical reasoning,
    safety checks, grounding verification, and multi-dimensional confidence scoring.
    """

    def __init__(
        self,
        policy_retriever: PolicyRetrievalInterface,
        evidence_engine: EvidenceEngine,
        reasoning_engine: ReasoningEngine,
        safety_guard: Any,  # Checked dynamically to prevent circular imports
        grounding_layer: Any,  # Checked dynamically
        hallucination_guard: Any,  # Checked dynamically
        confidence_scorer: Any,  # Checked dynamically
    ) -> None:
        self.policy_retriever = policy_retriever
        self.evidence_engine = evidence_engine
        self.reasoning_engine = reasoning_engine
        self.safety_guard = safety_guard
        self.grounding_layer = grounding_layer
        self.hallucination_guard = hallucination_guard
        self.confidence_scorer = confidence_scorer

    async def generate_recommendation(
        self,
        issue_id: str,
        issue_content: str,
        metadata: dict[str, Any],
        files: list[EvidenceFile],
    ) -> Recommendation:
        # Step 1: Input Safety Guard Check
        input_safe, input_categories = await self.safety_guard.check_text(issue_content)
        if not input_safe:
            # Short-circuit recommendation if input is unsafe
            from ai_platform.engines.reasoning import ReasoningStep

            reasoning_err = ReasoningOutcome(
                chain_of_thought=[
                    ReasoningStep(1, "Input check failed.", "Input flagged by safety.")
                ],
                verdict="REJECTED_UNSAFE",
                rationale=f"Citizen input flagged for safety violations: {input_categories}",
                policies_applied=[],
                grounding_references=[],
            )
            return Recommendation(
                recommendation_id=str(uuid.uuid4()),
                issue_id=issue_id,
                suggested_action="ROUTE_TO_HUMAN_SAFETY_OFFICER",
                priority_score=0.0,
                reasoning=reasoning_err,
                evidence_status="UNAUDITED",
                confidence_score=0.0,
                policies_consulted=[],
                safety_passed=False,
                grounding_score=0.0,
                hallucination_detected=False,
                metadata={"safety_flags": input_categories},
            )

        # Step 2: Policy Retrieval
        category = metadata.get("category", "")
        ward = metadata.get("ward", "")
        policies = await self.policy_retriever.retrieve_policies(
            context={"category": category, "ward": ward}, query=issue_content
        )
        policies_applied_ids = [p.policy_id for p in policies]

        # Step 3: Evidence Assessment
        # Dynamic required keys based on category
        required_evidence_schema = self._get_required_schema_for_category(category)
        evidence_assessment = await self.evidence_engine.assess_evidence(
            files, required_evidence_schema
        )

        # Step 4: Reasoning Engine Execution
        issue_payload = {
            "issue_id": issue_id,
            "content": issue_content,
            "metadata": metadata,
        }
        reasoning_outcome = await self.reasoning_engine.reason_about_issue(
            issue=issue_payload, policies=policies, evidence=evidence_assessment
        )

        # Step 5: Output Safety Guard Check
        output_safe, output_categories = await self.safety_guard.check_text(
            reasoning_outcome.rationale
        )
        final_safety_passed = input_safe and output_safe

        # Step 6: Grounding Verification
        grounding_result = await self.grounding_layer.verify_grounding(
            reasoning_outcome=reasoning_outcome,
            policies=policies,
            evidence=evidence_assessment,
        )
        grounding_score = grounding_result.grounding_score

        # Step 7: Hallucination Guard Check
        hallucination_detected = await self.hallucination_guard.detect_hallucinations(
            reasoning_outcome=reasoning_outcome, policies=policies
        )

        # Step 8: Multi-dimensional Confidence Scoring
        confidence = self.confidence_scorer.calculate_score(
            evidence_score=evidence_assessment.confidence_score,
            grounding_score=grounding_score,
            hallucination_detected=hallucination_detected,
            safety_passed=final_safety_passed,
        )

        # Step 9: Compile Recommendation Action
        suggested_action = self._determine_suggested_action(
            verdict=reasoning_outcome.verdict,
            evidence_sufficient=evidence_assessment.is_sufficient,
            hallucination_detected=hallucination_detected,
            safety_passed=final_safety_passed,
        )

        # Calculate Priority Score (0-100) based on severity factors in metadata and category
        priority_score = self._calculate_priority_score(metadata, suggested_action)

        return Recommendation(
            recommendation_id=str(uuid.uuid4()),
            issue_id=issue_id,
            suggested_action=suggested_action,
            priority_score=priority_score,
            reasoning=reasoning_outcome,
            evidence_status=(
                "SUFFICIENT" if evidence_assessment.is_sufficient else "INSUFFICIENT"
            ),
            confidence_score=confidence,
            policies_consulted=policies_applied_ids,
            safety_passed=final_safety_passed,
            grounding_score=grounding_score,
            hallucination_detected=hallucination_detected,
            metadata={
                "category": category,
                "ward": ward,
                "evidence_discrepancies": evidence_assessment.discrepancies,
                "grounding_warnings": grounding_result.warnings,
                "safety_output_flags": output_categories,
            },
        )

    def _get_required_schema_for_category(self, category: str) -> dict[str, Any]:
        if category == "sanitation":
            return {
                "required_keys": ["location", "waste_type"],
                "description": "Requires photo showing location landmarks and types of garbage.",
            }
        elif category == "roads":
            return {
                "required_keys": ["gps_coordinates", "pothole_dimensions_estimate"],
                "description": "Requires geotagged photos and dimensional assessment.",
            }
        else:
            return {
                "required_keys": ["description"],
                "description": "Basic narrative description required.",
            }

    def _determine_suggested_action(
        self,
        verdict: str,
        evidence_sufficient: bool,
        hallucination_detected: bool,
        safety_passed: bool,
    ) -> str:
        if not safety_passed:
            return "ROUTE_TO_HUMAN_SAFETY_OFFICER"
        if hallucination_detected:
            return "ROUTE_TO_HUMAN_RE-EVALUATION"
        if not evidence_sufficient:
            return "REQUEST_ADDITIONAL_EVIDENCE"

        if verdict == "APPROVE" or verdict == "VALIDATED":
            return "DISPATCH_FIELD_REPAIR"
        elif verdict == "REJECT" or verdict == "REJECTED":
            return "REJECT_COMPLAINT"
        else:
            return "ROUTE_TO_HUMAN_OPERATOR"

    def _calculate_priority_score(self, metadata: dict[str, Any], action: str) -> float:
        # Standard priority calculations based on category and user/location risk parameters
        if action in ["ROUTE_TO_HUMAN_SAFETY_OFFICER", "ROUTE_TO_HUMAN_RE-EVALUATION"]:
            return 80.0  # High priority for audit reviews

        base_priority = 50.0
        # Check severity indicator in metadata
        severity = metadata.get("severity", "medium").lower()
        if severity == "high":
            base_priority += 30.0
        elif severity == "low":
            base_priority -= 20.0

        # Specific category weights
        category = metadata.get("category", "")
        if category == "public_safety":
            base_priority += 15.0
        elif category == "infrastructure":
            base_priority += 10.0

        return min(max(base_priority, 0.0), 100.0)
