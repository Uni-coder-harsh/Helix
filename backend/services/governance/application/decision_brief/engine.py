import uuid
from typing import Any

from services.governance.application.agents.orchestration import (
    DecisionPipelineOrchestrator,
)
from services.governance.application.decision_brief.alternatives import (
    AlternativesEvaluator,
)
from services.governance.application.decision_brief.confidence import ConfidenceScorer
from services.governance.application.decision_brief.evidence import EvidenceExtractor
from services.governance.application.decision_brief.explanation import (
    ExplanationGenerator,
)


class DecisionBriefEngine:
    """Orchestrates multi-agent execution results to compile an Explainable Governance Decision Brief."""

    def __init__(self) -> None:
        self.orchestrator = DecisionPipelineOrchestrator()
        self.explanation_gen = ExplanationGenerator()

    async def generate_brief(self, issue: dict[str, Any]) -> dict[str, Any]:
        # 1. Run the sequential agent pipeline to construct context
        pipeline_result = await self.orchestrator.run_pipeline(issue)

        # Merge outputs from all successful agent steps into a flat context dictionary
        context: dict[str, Any] = {}
        for step in pipeline_result.get("timeline", []):
            if step.get("status") == "SUCCESS":
                context.update(step.get("outputs", {}))

        # Preserve issue values inside context
        context["latitude"] = issue.get("latitude")
        context["longitude"] = issue.get("longitude")

        # 2. Extract Evidence & Proximity Assets
        evidence_list = EvidenceExtractor.extract_evidence(context)
        nearby_assets = EvidenceExtractor.get_nearby_assets(context)

        # 3. Extract matched policies and schemes
        matched_policy = context.get("matched_policy")
        matched_scheme = context.get("matched_scheme")

        applicable_policies = (
            [{"name": matched_policy, "code": "REG-2024-09"}] if matched_policy else []
        )
        applicable_schemes = (
            [{"name": matched_scheme, "subsidy_ratio": 0.60}] if matched_scheme else []
        )

        # 4. Alternatives Evaluation
        alternatives = AlternativesEvaluator.get_alternatives(
            category=issue.get("category", ""),
            issue_description=issue.get("description", ""),
        )

        # 5. LLM-Grounding Reasoning & Follow-up Actions
        explanation = await self.explanation_gen.generate_explanation(
            category=issue.get("category", ""),
            title=issue.get("title", ""),
            description=issue.get("description", ""),
            context=context,
        )

        # 6. Hybrid Confidence Score
        confidence = ConfidenceScorer.compute_confidence(
            context=context, llm_confidence=explanation.get("llm_confidence")
        )

        # 7. Package structured response
        import datetime

        return {
            "brief_id": str(uuid.uuid4()),
            "version": "1.0.0",
            "generated_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "generated_by": "Helix AI Decision Engine",
            "issue_id": str(issue.get("id", "")),
            "problem": {
                "id": str(issue.get("id", "")),
                "title": issue.get("title", ""),
                "description": issue.get("description", ""),
                "category": issue.get("category", ""),
                "location": {
                    "latitude": issue.get("latitude"),
                    "longitude": issue.get("longitude"),
                },
                "status": issue.get("status", "INGESTED"),
                "priority": issue.get("priority", "MEDIUM"),
            },
            "evidence": evidence_list,
            "nearby_assets": nearby_assets,
            "applicable_policies": applicable_policies,
            "applicable_schemes": applicable_schemes,
            "impact_summary": {
                "affected_population": context.get("affected_population", 150),
                "urgency_score": context.get("urgency_score", 0.60),
                "severity_level": context.get("priority", "MEDIUM"),
            },
            "alternative_actions": alternatives,
            "recommendation": {
                "suggested_department": context.get(
                    "suggested_department", "Public Works Department"
                ),
                "recommended_action": context.get(
                    "recommended_action", "Dispatch Road restoration crew"
                ),
                "estimated_cost": context.get("estimated_cost", "₹1.5 Lakhs"),
                "sla": context.get("sla", "48 Hours"),
            },
            "reasoning": explanation.get("reasoning", []),
            "confidence": confidence,
            "follow_up_actions": explanation.get("follow_up_actions", []),
        }
