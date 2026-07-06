from services.governance.application.planning.outcome_engine import (
    OutcomePlanningEngine,
)


def test_outcome_planning_generation() -> None:
    engine = OutcomePlanningEngine()

    mock_issues = [
        {
            "category": "Water Supply & Sanitation",
            "latitude": 12.95,
            "longitude": 77.60,
        },
        {"category": "Roads & Sidewalks", "latitude": 12.96, "longitude": 77.61},
    ]

    projects = engine.plan_projects(mock_issues)

    assert len(projects) == 2
    assert "Drainage & Water Pipe" in projects[0]["title"]
    assert "Pedestrian Corridor" in projects[1]["title"]
    assert projects[0]["cost"] == "₹1.8 Crores"
    assert projects[0]["confidence"] == 0.93
    assert projects[0]["evidence_count"] == 1
    assert (
        " Shivaji Nagar Hospital" in projects[0]["explanation"]
        or len(projects[0]["explanation"]) > 20
    )

    # Verify outcomes simulation mapping
    outcomes = projects[0]["outcomes"]
    assert len(outcomes) == 3
    assert outcomes[0]["metric"] == "Water Health Index"
    assert outcomes[0]["before"] == 61
    assert outcomes[0]["after"] == 83
