from helix_platform.persistence import SessionLocal
from services.governance.application.spatial.constituency_health import (
    ConstituencyHealthEngine,
)
from services.governance.application.spatial.hotspot_engine import HotspotEngine
from services.governance.application.spatial.service import (
    SpatialIntelligenceService,
)
from services.governance.infrastructure.queries import SQLAlchemyGovernanceQueryService


def test_constituency_health_derived_scoring() -> None:
    # 1. Base health calculation
    issues = [
        {"category": "Water Supply & Sanitation", "priority": "High"},
        {"category": "Water Supply & Sanitation", "priority": "Low"},
        {"category": "Roads & Sidewalks", "priority": "Medium"},
    ]
    res = ConstituencyHealthEngine.calculate_health_scores(issues)
    assert res["overall_health_score"] < 100
    assert res["category_scores"]["Water Supply & Sanitation"] == 94  # 100 - (5 + 1)
    assert res["category_scores"]["Roads & Sidewalks"] == 97  # 100 - 3


def test_hotspot_proposal_logic() -> None:
    # 2. Check if two nearby issues group into a single project proposal
    issues = [
        {
            "id": "complaint-1",
            "category": "Water Supply & Sanitation",
            "latitude": 12.9750,
            "longitude": 77.5950,
        },
        {
            "id": "complaint-2",
            "category": "Water Supply & Sanitation",
            "latitude": 12.9760,
            "longitude": 77.5960,
        },
        {
            "id": "complaint-3",
            "category": "Roads & Sidewalks",  # Different category, won't merge
            "latitude": 12.9750,
            "longitude": 77.5950,
        },
    ]

    hotspots = HotspotEngine.identify_hotspots(issues, radius_km=0.35)
    assert len(hotspots) == 1
    assert hotspots[0]["complaints_count"] == 2
    assert (
        hotspots[0]["proposed_project"]["title"] == "Reconstruct Main Water Pipe Trunk"
    )
    assert "complaint-1" in hotspots[0]["linked_complaint_ids"]
    assert "complaint-2" in hotspots[0]["linked_complaint_ids"]


def test_spatial_intelligence_service() -> None:
    db = SessionLocal()
    query_svc = SQLAlchemyGovernanceQueryService(db)
    spatial_svc = SpatialIntelligenceService(query_svc)

    overview = spatial_svc.get_constituency_overview()
    assert "overall_health_score" in overview
    assert "category_scores" in overview
    assert "hotspots" in overview
    assert "risk_zones" in overview

    dataset = spatial_svc.get_map_dataset()
    assert "boundaries" in dataset
    assert "heatmap" in dataset
    assert "clusters" in dataset
    assert "hotspots" in dataset
