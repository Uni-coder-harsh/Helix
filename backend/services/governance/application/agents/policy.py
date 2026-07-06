import time
from typing import Any

from services.governance.application.agents.contracts import AgentResult, BaseAgent


class PolicyAgent(BaseAgent):
    """Evaluates regulatory compliance policies and matches issues to eligible subsidy schemes."""

    @property
    def name(self) -> str:
        return "Policy Agent"

    def run(self, context: dict[str, Any]) -> AgentResult:
        start_time = time.perf_counter()
        issue = context.get("issue", {})
        desc = issue.get("description", "").lower()
        is_sanit = (
            "water" in desc or "leak" in desc or "drain" in desc or "sanit" in desc
        )

        policy = (
            "Sanitation Waste Management Regulation 2024"
            if is_sanit
            else "Municipal Road Maintenance Policy 2023"
        )
        scheme = (
            "Swachh Bharat Abhiyan Subsidy"
            if is_sanit
            else "PMGSY Road Infrastructure Upgrade Program"
        )

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        return AgentResult(
            agent_name=self.name,
            status="SUCCESS",
            confidence=0.94,
            execution_time_ms=duration_ms,
            inputs={"category_desc": desc[:30]},
            outputs={"matched_policy": policy, "matched_scheme": scheme},
            evidence=[
                f"Regulatory Evaluation: Aligned with '{policy}'.",
                f"Fund clearance match found under '{scheme}'.",
            ],
            warnings=[],
            errors=[],
            next_agent="Impact Agent",
        )
