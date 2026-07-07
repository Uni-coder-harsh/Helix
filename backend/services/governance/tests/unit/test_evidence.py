import datetime
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from helix_platform.persistence import Base
from services.governance.application.evidence.clustering import (
    ClusteringEngine,
)
from services.governance.application.evidence.duplicate_detector import (
    DuplicateDetector,
)
from services.governance.application.evidence.image_match import (
    calculate_image_similarity,
)
from services.governance.application.evidence.service import (
    EvidenceIntelligenceService,
)
from services.governance.application.evidence.similarity import (
    calculate_haversine_distance,
    calculate_text_similarity,
)
from services.governance.infrastructure.models import IncidentDB, IssueDB


# InMemory SQLite Setup for Unit Tests
@pytest.fixture(name="db_session")
def fixture_db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()


def test_similarity_math():
    # Text similarity ratios
    assert (
        calculate_text_similarity("Pothole Shivaji Road", "Pothole Shivaji Road") == 1.0
    )
    assert (
        calculate_text_similarity("Pothole Shivaji Road", "Clean Street Shivaji Nagar")
        < 0.6
    )
    assert calculate_text_similarity("", "Something") == 0.0

    # Haversine distance calculations
    # Shivaji Nagar coordinates
    dist = calculate_haversine_distance(12.9755, 77.5955, 12.9755, 77.5955)
    assert dist == 0.0

    # Approx 111m distance for 0.001 lat diff
    dist_diff = calculate_haversine_distance(12.9755, 77.5955, 12.9765, 77.5955)
    assert 100 < dist_diff < 120

    # Image similarity basenames
    assert (
        calculate_image_similarity("/tmp/path/a.jpg", "https://img.com/a.jpg") == 0.95
    )
    assert calculate_image_similarity("/tmp/path/a.jpg", "/tmp/path/b.jpg") == 0.5


def test_duplicate_detector():
    detector = DuplicateDetector()

    now = datetime.datetime.now(datetime.UTC)
    issue1 = {
        "title": "Broken pipe leaking water",
        "description": "A major water leak near Shivaji School has flooded the main street.",
        "category": "Water Supply & Sanitation",
        "latitude": 12.9755,
        "longitude": 77.5955,
        "created_at": now,
    }

    # Exact duplicate
    conf, breakdown = detector.calculate_confidence(issue1, issue1)
    assert conf == 1.0
    assert breakdown["spatial"] == 1.0
    assert breakdown["text"] == 1.0

    # High similarity duplicate (close coordinate, similar text, same category)
    issue2 = {
        "title": "Water leakage and flooding",
        "description": "Leaking pipe near Shivaji School has caused massive flooding on the road.",
        "category": "Water Supply & Sanitation",
        "latitude": 12.9758,  # very close (approx 33m)
        "longitude": 77.5957,
        "created_at": now + datetime.timedelta(hours=2),
    }
    conf2, breakdown2 = detector.calculate_confidence(issue1, issue2)
    assert conf2 > 0.75
    assert breakdown2["spatial"] > 0.80
    assert breakdown2["category"] == 1.0

    # Dissimilar issue (far away, different category, different text)
    issue3 = {
        "title": "Streetlight broken",
        "description": "Dark streetlight segment in Sector 4 is causing safety problems.",
        "category": "Electricity & Streetlights",
        "latitude": 12.9999,
        "longitude": 77.6200,
        "created_at": now - datetime.timedelta(days=15),
    }
    conf3, breakdown3 = detector.calculate_confidence(issue1, issue3)
    assert conf3 < 0.30
    assert breakdown3["category"] == 0.0


def test_clustering_engine():
    engine = ClusteringEngine(match_threshold=0.75)

    now = datetime.datetime.now(datetime.UTC)
    canon = {
        "id": "canon-1",
        "title": "Water Main Leakage",
        "description": "Leaking pipe segment flooding Shivaji Nagar segment.",
        "category": "Water Supply & Sanitation",
        "latitude": 12.9755,
        "longitude": 77.5955,
        "created_at": now,
    }

    incidents = [{"id": "inc-1", "title": "Incident: Water Main Leakage"}]
    canonical_issues = {"inc-1": canon}

    # Matches incident 1
    matching_issue = {
        "title": "Flooded street due to leaking water pipe",
        "description": "Leaking pipe segment flooding Shivaji Nagar segment.",
        "category": "Water Supply & Sanitation",
        "latitude": 12.9756,
        "longitude": 77.5956,
        "created_at": now,
    }
    best_match, conf, _breakdown = engine.find_best_incident_match(
        matching_issue, incidents, canonical_issues
    )
    assert best_match is not None
    assert best_match["id"] == "inc-1"
    assert conf >= 0.75

    # Does not match incident 1 (different location/category)
    different_issue = {
        "title": "Pothole in road",
        "description": "Large road crater in Sector 4.",
        "category": "Roads & Footpaths",
        "latitude": 12.9990,
        "longitude": 77.6200,
        "created_at": now,
    }
    best_match2, _conf2, _breakdown2 = engine.find_best_incident_match(
        different_issue, incidents, canonical_issues
    )
    assert best_match2 is None


def test_evidence_intelligence_service(db_session):
    service = EvidenceIntelligenceService()

    # 1. Seed two similar issues
    issue1 = IssueDB(
        id=str(uuid.uuid4()),
        citizen_id=str(uuid.uuid4()),
        title="Pothole Shivaji Road",
        description="Very large pothole near Shivaji Nagar Primary School.",
        category="Roads & Footpaths",
        latitude=12.9755,
        longitude=77.5955,
        location_address="Shivaji Road, Bengaluru",
    )
    db_session.add(issue1)
    db_session.commit()

    # Auto cluster first issue -> Should create a brand new Incident
    res1 = service.auto_cluster_issue(issue1.id, db_session)
    assert res1["created_new"] is True
    assert res1["incident_id"] is not None

    # Query incident
    inc = (
        db_session.query(IncidentDB)
        .filter(IncidentDB.id == res1["incident_id"])
        .first()
    )
    assert inc is not None
    assert inc.title == "Incident Cluster: Pothole Shivaji Road"

    # 2. Add a second matching issue
    issue2 = IssueDB(
        id=str(uuid.uuid4()),
        citizen_id=str(uuid.uuid4()),
        title="Big pothole in road segment",
        description="Leaking potholes near Shivaji School.",
        category="Roads & Footpaths",
        latitude=12.9756,
        longitude=77.5956,
        location_address="Shivaji Road, Bengaluru",
    )
    db_session.add(issue2)
    db_session.commit()

    # Auto cluster second issue -> Should merge into existing Incident
    res2 = service.auto_cluster_issue(issue2.id, db_session)
    assert res2["created_new"] is False
    assert res2["incident_id"] == inc.id
    assert res2["confidence"] > 0.70

    # 3. Retrieve duplicates list for issue 1
    dups = service.get_issue_duplicates(issue1.id, db_session)
    assert len(dups) == 1
    assert dups[0]["issue"]["id"] == issue2.id
    assert dups[0]["already_merged"] is True

    # 4. Incident details aggregation check
    details = service.get_incident_details(inc.id, db_session)
    assert details["reports_count"] == 2
    assert len(details["reports"]) == 2

    # 5. Relationship Graph check
    graph = service.get_relationship_graph(db_session)
    assert len(graph["nodes"]) == 3  # 1 incident + 2 issues
    assert len(graph["edges"]) == 2  # both belong_to edges
