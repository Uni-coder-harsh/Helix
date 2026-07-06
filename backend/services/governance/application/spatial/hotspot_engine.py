import uuid
from typing import Any

from helix_platform.spatial import GeoService


class HotspotEngine:
    """Groups issues within a radius and proposes a single developmental project to solve them."""

    @staticmethod
    def identify_hotspots(
        issues: list[dict[str, Any]], radius_km: float = 0.35
    ) -> list[dict[str, Any]]:
        hotspots = []
        visited = set()

        for i, issue in enumerate(issues):
            if i in visited:
                continue

            category = issue["category"]
            cluster_members = [issue]
            visited.add(i)

            # Find matching category issues nearby
            for j, other in enumerate(issues):
                if j in visited:
                    continue

                if other["category"] != category:
                    continue

                dist = GeoService.calculate_distance(
                    issue["latitude"],
                    issue["longitude"],
                    other["latitude"],
                    other["longitude"],
                )
                if dist <= radius_km:
                    cluster_members.append(other)
                    visited.add(j)

            # If there are multiple complaints (e.g. 2+), form a Hotspot project proposal
            if len(cluster_members) >= 2:
                avg_lat = sum(m["latitude"] for m in cluster_members) / len(
                    cluster_members
                )
                avg_lng = sum(m["longitude"] for m in cluster_members) / len(
                    cluster_members
                )

                # Propose signature developmental projects rather than individual fixes
                is_sanitation = (
                    "sanit" in category.lower() or "water" in category.lower()
                )
                project_title = (
                    "Reconstruct Main Water Pipe Trunk"
                    if is_sanitation
                    else "Full Sidewalk & Corridor Reconstruction"
                )
                project_cost = "₹18 Lakhs" if is_sanitation else "₹12 Lakhs"
                project_duration = "45 Days" if is_sanitation else "30 Days"

                # Estimate population based on member density
                affected_pop = len(cluster_members) * 240 + 800

                hotspots.append(
                    {
                        "id": str(uuid.uuid4()),
                        "category": category,
                        "latitude": avg_lat,
                        "longitude": avg_lng,
                        "complaints_count": len(cluster_members),
                        "affected_population": affected_pop,
                        "linked_complaint_ids": [str(m["id"]) for m in cluster_members],
                        "proposed_project": {
                            "title": project_title,
                            "estimated_cost": project_cost,
                            "estimated_duration": project_duration,
                            "impact": "High developmental index resolution",
                        },
                    }
                )

        return hotspots
