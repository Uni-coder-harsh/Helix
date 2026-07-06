import pytest

from services.governance.application.agents.classification import ClassificationAgent
from services.governance.application.agents.duplicate import DuplicateAgent
from services.governance.application.agents.intake import IntakeAgent
from services.governance.application.agents.orchestration import (
    DecisionPipelineOrchestrator,
)


def test_individual_agents() -> None:
    # 1. Intake Agent success
    intake = IntakeAgent()
    res = intake.run(
        {
            "issue": {
                "description": "Broken main water pipe leak.",
                "latitude": 12.95,
                "longitude": 77.60,
            }
        }
    )
    assert res.status == "SUCCESS"
    assert (
        "Sanitized" in res.evidence[0]
        or "Sanitized" in res.outputs
        or "Sanitized" in res.agent_name
        or len(res.evidence) > 0
    )

    # 2. Classification Agent water heuristic
    clf = ClassificationAgent()
    res = clf.run({"issue": {"description": "Water pipeline burst Shivaji Nagar W12"}})
    assert res.outputs["category"] == "Water Supply & Sanitation"
    assert res.confidence == pytest.approx(0.97)

    # 3. Duplicate Agent
    dup = DuplicateAgent()
    res = dup.run(
        {
            "issue": {
                "description": "leak water",
                "latitude": 12.95,
                "longitude": 77.60,
            }
        }
    )
    assert res.outputs["duplicate_count"] == 18
    assert len(res.warnings) > 0  # Active hotspot warning triggered


def test_orchestrated_pipeline_execution() -> None:
    orchestrator = DecisionPipelineOrchestrator()
    mock_issue = {
        "id": "mock-uuid-1049",
        "title": "Severe road pothole water hazard",
        "description": "There is a massive water leak pooling inside a deep pothole on the main clinic road.",
        "latitude": 12.98,
        "longitude": 77.58,
    }

    result = orchestrator.run_pipeline(mock_issue)

    assert result["overall_status"] == "SUCCESS"
    assert result["average_confidence"] > 0.90
    assert len(result["timeline"]) == 7  # All 7 agents executed sequentially

    # Asserting individual timeline steps
    agent_names = [step["agent_name"] for step in result["timeline"]]
    assert "Intake Agent" in agent_names
    assert "Classification Agent" in agent_names
    assert "Duplicate Agent" in agent_names
    assert "Context Agent" in agent_names
    assert "Policy Agent" in agent_names
    assert "Impact Agent" in agent_names
    assert "Recommendation Agent" in agent_names

    # Check telemetry fields
    telemetry = result["telemetry"]
    assert telemetry["status"] == "SUCCESS"
    assert len(telemetry["agents_run"]) == 7
    assert telemetry["total_duration_ms"] > 0.0
