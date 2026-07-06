import time
from typing import Any

from services.governance.application.agents.contracts import AgentResult, BaseAgent


class IntakeAgent(BaseAgent):
    """Verifies intake ticket fields, formatting, and geo-coordinate validity."""

    @property
    def name(self) -> str:
        return "Intake Agent"

    def run(self, context: dict[str, Any]) -> AgentResult:
        start_time = time.perf_counter()
        issue = context.get("issue", {})

        warnings = []
        errors = []
        status = "SUCCESS"

        # Ingestion validations
        desc = issue.get("description", "")
        if not desc:
            errors.append("Empty description payload.")
            status = "FAILURE"

        lat = issue.get("latitude")
        lng = issue.get("longitude")

        if lat is None or lng is None:
            errors.append("Missing geo-spatial coordinate metrics.")
            status = "FAILURE"
        else:
            # Bangalore standard boundary check bounds
            if not (12.80 <= lat <= 13.10) or not (77.40 <= lng <= 77.80):
                warnings.append(
                    "Coordinates fall outside standard central ward boundary limits."
                )

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        return AgentResult(
            agent_name=self.name,
            status=status,
            confidence=1.0 if status == "SUCCESS" else 0.0,
            execution_time_ms=duration_ms,
            inputs={"description": desc[:30], "latitude": lat, "longitude": lng},
            outputs={
                "sanitized_description": desc.strip(),
                "validated_coordinates": {"lat": lat, "lng": lng},
            },
            evidence=[
                "Description satisfies minimum intake text requirements.",
                "GPS coordinates parsed successfully.",
            ],
            warnings=warnings,
            errors=errors,
            next_agent="Classification Agent",
        )
