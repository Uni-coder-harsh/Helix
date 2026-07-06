import time
import uuid
from typing import Any

from services.governance.application.agents.classification import ClassificationAgent
from services.governance.application.agents.context import ContextAgent
from services.governance.application.agents.contracts import AgentResult
from services.governance.application.agents.duplicate import DuplicateAgent
from services.governance.application.agents.impact import ImpactAgent
from services.governance.application.agents.intake import IntakeAgent
from services.governance.application.agents.policy import PolicyAgent
from services.governance.application.agents.recommendation import RecommendationAgent


class DecisionPipelineOrchestrator:
    """Orchestrates sequential execution of policy decision agents and collects telemetry."""

    def __init__(self) -> None:
        self.agents = [
            IntakeAgent(),
            ClassificationAgent(),
            DuplicateAgent(),
            ContextAgent(),
            PolicyAgent(),
            ImpactAgent(),
            RecommendationAgent(),
        ]

    def run_pipeline(self, issue: dict[str, Any]) -> dict[str, Any]:
        pipeline_id = uuid.uuid4()
        start_time = time.perf_counter()

        results: list[AgentResult] = []
        context = {"issue": issue}

        # Sequentially execute agents
        for agent in self.agents:
            try:
                res = agent.run(context)
                results.append(res)
                # Feed outputs of current agent into downstream agent context
                context.update(res.outputs)
                if res.status == "FAILURE":
                    break
            except Exception as e:
                # Handle unexpected execution errors gracefully
                results.append(
                    AgentResult(
                        agent_name=agent.name,
                        status="FAILURE",
                        confidence=0.0,
                        errors=[str(e)],
                    )
                )
                break

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        # Calculate summary metrics
        total_latency = sum(r.execution_time_ms for r in results)
        avg_confidence = (
            sum(r.confidence for r in results) / len(results) if results else 0.0
        )

        # Structured Telemetry Log
        telemetry = {
            "pipeline_id": str(pipeline_id),
            "issue_id": str(issue.get("id", "")),
            "agents_run": [r.agent_name for r in results],
            "total_duration_ms": duration_ms,
            "token_usage_placeholder": 0,
            "cost_placeholder": 0.0,
            "average_confidence": avg_confidence,
            "status": (
                "SUCCESS" if all(r.status == "SUCCESS" for r in results) else "FAILURE"
            ),
        }

        return {
            "pipeline_id": str(pipeline_id),
            "issue_id": str(issue.get("id", "")),
            "overall_status": telemetry["status"],
            "total_latency_ms": total_latency,
            "average_confidence": avg_confidence,
            "timeline": [r.model_dump() for r in results],
            "telemetry": telemetry,
        }
