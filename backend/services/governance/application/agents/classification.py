import time
from typing import Any

from services.governance.application.agents.contracts import AgentResult, BaseAgent


class ClassificationAgent(BaseAgent):
    """Categorizes issues based on token checking heuristics and reports categorization confidence."""

    @property
    def name(self) -> str:
        return "Classification Agent"

    def run(self, context: dict[str, Any]) -> AgentResult:
        start_time = time.perf_counter()
        issue = context.get("issue", {})
        desc = issue.get("description", "").lower()

        # Simple classification heuristics
        if (
            "water" in desc
            or "leak" in desc
            or "drain" in desc
            or "sanit" in desc
            or "garbage" in desc
            or "waste" in desc
        ):
            category = "Water Supply & Sanitation"
            confidence = 0.97
            evidence = ["Matched sanitation keywords: water/leak/waste in description."]
        elif (
            "road" in desc
            or "pothole" in desc
            or "sidewalk" in desc
            or "pavement" in desc
            or "street" in desc
        ):
            category = "Roads & Sidewalks"
            confidence = 0.95
            evidence = [
                "Matched transit keywords: road/pothole/sidewalk in description."
            ]
        else:
            category = "General Civil Maintenance"
            confidence = 0.85
            evidence = ["No matched keyword subclass; classified under General Civil."]

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        return AgentResult(
            agent_name=self.name,
            status="SUCCESS",
            confidence=confidence,
            execution_time_ms=duration_ms,
            inputs={"description_sample": desc[:40]},
            outputs={"category": category},
            evidence=evidence,
            warnings=[],
            errors=[],
            next_agent="Duplicate Agent",
        )
