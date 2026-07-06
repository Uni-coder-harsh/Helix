from typing import Any

from helix_platform.spatial import GeoService, IssueClustering
from services.governance.application.queries import GovernanceQueryService
from services.governance.application.spatial.constituency_health import (
    ConstituencyHealthEngine,
)
from services.governance.application.spatial.hotspot_engine import HotspotEngine


class SpatialIntelligenceService:
    """Master application service orchestrating spatial health scores, hotspots, and map visualization layers."""

    def __init__(self, query_service: GovernanceQueryService) -> None:
        self.query_service = query_service
        self.geo_service = GeoService()

    def get_constituency_overview(self) -> dict[str, Any]:
        """Calculates derived health metrics, risk zones, and priority hotspots."""
        issues = self.query_service.list_pending_issues()
        health = ConstituencyHealthEngine.calculate_health_scores(issues)
        hotspots = HotspotEngine.identify_hotspots(issues, radius_km=0.35)

        # Risk Zones based on critical issues count
        critical_count = len(
            [
                i
                for i in issues
                if i.get("priority") in ["Critical", "High", "HIGH", "CRITICAL"]
            ]
        )

        return {
            "constituency_name": "Bangalore Central Constituency",
            "overall_health_score": health["overall_health_score"],
            "overall_health_trend": health["overall_health_trend"],
            "category_scores": health["category_scores"],
            "hotspots": hotspots,
            "risk_zones": [
                {
                    "name": "Shivaji Nagar Sector B",
                    "risk_rating": "HIGH" if critical_count > 0 else "MEDIUM",
                    "reason": f"Active cluster of {critical_count} unresolved critical alerts.",
                }
            ],
            "total_pending_issues": len(issues),
        }

    def get_map_dataset(self) -> dict[str, Any]:
        """Compiles boundaries, clusters, heatmaps, and hotspots into a unified dataset for mapping."""
        issues = self.query_service.list_pending_issues()

        boundaries = self.geo_service.get_boundaries_as_geojson()
        heatmap = self.geo_service.generate_heatmap_data(issues)
        clusters = IssueClustering.cluster_issues(issues, radius_km=0.5)
        hotspots = HotspotEngine.identify_hotspots(issues, radius_km=0.35)

        return {
            "boundaries": boundaries,
            "heatmap": heatmap,
            "clusters": clusters,
            "hotspots": hotspots,
        }
