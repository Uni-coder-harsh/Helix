import math
from typing import Any


class SpatialIndex:
    """In-memory spatial index representing geographical points and bound checks."""

    def __init__(self) -> None:
        # Static boundary polygons (mock coordinates enclosing Shivaji Nagar / Central Bangalore)
        self.ward_boundaries = {
            "Shivaji Nagar (Ward 12)": [
                (12.9700, 77.5900),
                (12.9800, 77.5900),
                (12.9800, 77.6000),
                (12.9700, 77.6000),
            ]
        }
        self.constituency_boundaries = {
            "Bangalore Central": [
                (12.9500, 77.5700),
                (12.9900, 77.5700),
                (12.9900, 77.6200),
                (12.9500, 77.6200),
            ]
        }

    def is_inside_polygon(
        self, lat: float, lon: float, polygon: list[tuple[float, float]]
    ) -> bool:
        """Ray-casting algorithm to determine if a point is inside a polygon boundary."""
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if (
                (lon > min(p1y, p2y))
                and (lon <= max(p1y, p2y))
                and (lat <= max(p1x, p2x))
            ):
                if p1y != p2y:
                    xinters = (lon - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or lat <= xinters:
                    inside = not inside
            p1x, p1y = p2x, p2y
        return inside


class GeoService:
    """Service handling distance metrics, GeoJSON translations, and heatmap outputs."""

    def __init__(self, index: SpatialIndex | None = None) -> None:
        self.index = index or SpatialIndex()

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine formula to compute great-circle distance in kilometers."""
        r = 6371.0  # Earth radius in kilometers
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (
            math.sin(d_lat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(d_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    def get_boundaries_as_geojson(self) -> dict[str, Any]:
        """Translates boundaries metadata to standard GeoJSON FeatureCollection."""
        features = []
        # Add Ward boundaries
        for name, polygon in self.index.ward_boundaries.items():
            # Format coordinates as GeoJSON LineString / Polygon rings [lon, lat]
            coords = [[p[1], p[0]] for p in polygon]
            coords.append(coords[0])  # Close ring
            features.append(
                {
                    "type": "Feature",
                    "properties": {"name": name, "level": "ward"},
                    "geometry": {"type": "Polygon", "coordinates": [coords]},
                }
            )

        # Add Constituency boundaries
        for name, polygon in self.index.constituency_boundaries.items():
            coords = [[p[1], p[0]] for p in polygon]
            coords.append(coords[0])
            features.append(
                {
                    "type": "Feature",
                    "properties": {"name": name, "level": "constituency"},
                    "geometry": {"type": "Polygon", "coordinates": [coords]},
                }
            )

        return {"type": "FeatureCollection", "features": features}

    def generate_heatmap_data(
        self, issues: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Aggregates geolocations of issues to produce weighted heatmap points."""
        points = []
        for issue in issues:
            points.append(
                {
                    "lat": issue["latitude"],
                    "lng": issue["longitude"],
                    "weight": 1.0 if issue.get("priority", "LOW") == "LOW" else 2.5,
                }
            )
        return points


class IssueClustering:
    """Clustering service that groups nearby markers to prevent map overcrowding."""

    @staticmethod
    def cluster_issues(
        issues: list[dict[str, Any]], radius_km: float = 0.5
    ) -> list[dict[str, Any]]:
        """Clusters complaints situated closer than radius_km into grouped nodes."""
        clustered = []
        visited = set()

        for i, issue in enumerate(issues):
            if i in visited:
                continue

            cluster_members = [issue]
            visited.add(i)

            # Find nearby unvisited issues
            for j, other in enumerate(issues):
                if j in visited:
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

            # Calculate center coordinate of cluster
            avg_lat = sum(m["latitude"] for m in cluster_members) / len(cluster_members)
            avg_lng = sum(m["longitude"] for m in cluster_members) / len(
                cluster_members
            )

            if len(cluster_members) > 1:
                clustered.append(
                    {
                        "type": "cluster",
                        "latitude": avg_lat,
                        "longitude": avg_lng,
                        "count": len(cluster_members),
                        "ids": [m["id"] for m in cluster_members],
                    }
                )
            else:
                clustered.append(
                    {
                        "type": "single",
                        "id": issue["id"],
                        "latitude": issue["latitude"],
                        "longitude": issue["longitude"],
                        "title": issue["title"],
                        "category": issue["category"],
                    }
                )

        return clustered
