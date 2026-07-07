from services.governance.application.timeline.engine import TimelineEngine
from services.governance.application.timeline.events import EVENT_CATALOG, TimelineStage
from services.governance.application.timeline.formatter import TimelineFormatter


def test_event_catalog_structure():
    assert "REPORTED" in EVENT_CATALOG
    assert "CLOSED" in EVENT_CATALOG
    assert EVENT_CATALOG["REPORTED"]["stage"] == TimelineStage.INTAKE.value


def test_timeline_formatter_citizen_role():
    entries = [
        {
            "id": "1",
            "actor": "Citizen (Mobile App)",
            "action": "REPORTED",
            "visibility": ["citizen", "officer"],
            "description": "Lodge complaint",
        },
        {
            "id": "2",
            "actor": "Duplicate Agent",
            "action": "DUPLICATE_SCANNED",
            "visibility": ["officer"],
            "description": "Scan duplicates",
        },
    ]
    res = TimelineFormatter.format_timeline(entries, "citizen")
    assert len(res) == 1
    assert res[0]["action"] == "REPORT_SUBMITTED"
    assert res[0]["actor"] == "Citizen"


def test_timeline_formatter_officer_role():
    entries = [
        {
            "id": "1",
            "actor": "Citizen (Mobile App)",
            "action": "REPORTED",
            "visibility": ["citizen", "officer"],
            "description": "Lodge complaint",
        },
        {
            "id": "2",
            "actor": "Duplicate Agent",
            "action": "DUPLICATE_SCANNED",
            "visibility": ["officer"],
            "description": "Scan duplicates",
        },
    ]
    res = TimelineFormatter.format_timeline(entries, "officer")
    assert len(res) == 2


def test_timeline_generation_ingested_issue():
    issue = {
        "id": "mock-uuid-1",
        "title": "Broken road block",
        "description": "Massive pothole at crossroads",
        "category": "Roads & Sidewalks",
        "status": "INGESTED",
        "created_at": "2026-07-07T12:00:00Z",
    }

    # Check citizen view
    timeline_citizen = TimelineEngine.generate_timeline(issue, role="citizen")
    assert timeline_citizen["progress"] == 10
    # In citizen view, we should see:
    # 1. REPORTED -> mapped to REPORT_SUBMITTED
    # 2. UNDER_REVIEW (citizen only) -> mapped to UNDER_REVIEW
    # 3. OFFICER_REVIEWED -> mapped to UNDER_REVIEW
    # 4. DISPATCHED -> mapped to DEPARTMENT_ASSIGNED
    # 5. WORK_STARTED -> mapped to WORK_IN_PROGRESS (PENDING, but present)
    # 6. RESOLVED -> mapped to COMPLETED (PENDING, but present)
    # 7. CLOSED -> mapped to FEEDBACK_REQUESTED (PENDING, but present)
    # Total visible: 9 entries
    assert len(timeline_citizen["timeline"]) == 9

    # Check officer view
    timeline_officer = TimelineEngine.generate_timeline(issue, role="officer")
    assert timeline_officer["progress"] == 10
    # For officer: Reported, Duplicate, Classified, Spatial, Policy, Brief,
    # Officer Review, Dispatch, Field Dispatch, Work Started, Resolved, Verified, Closed, plus 3 duplicate clustering events.
    # Total: 16 entries
    assert len(timeline_officer["timeline"]) == 16

    # Validate ordering
    timestamps = [
        e["timestamp"]
        for e in timeline_officer["timeline"]
        if e["timestamp"] is not None
    ]
    assert len(timestamps) > 0
    sorted_timestamps = sorted(timestamps)
    assert timestamps == sorted_timestamps


def test_timeline_generation_closed_issue():
    issue = {
        "id": "mock-uuid-2",
        "title": "Water leaking",
        "description": "Pipe burst under road",
        "category": "Sanitation & Waste",
        "status": "CLOSED",
        "created_at": "2026-07-07T12:00:00Z",
    }

    timeline_officer = TimelineEngine.generate_timeline(issue, role="officer")
    assert timeline_officer["progress"] == 100

    # Find closed event in timeline
    closed_event = next(
        e for e in timeline_officer["timeline"] if e["action"] == "CLOSED"
    )
    assert closed_event["status"] == "COMPLETED"
    assert closed_event["metadata"]["constituency_health_delta"] == 0.04
    assert "outcome_connection" in closed_event["metadata"]
    assert (
        closed_event["metadata"]["outcome_connection"]["linked_project"]["status"]
        == "COMPLETED"
    )
