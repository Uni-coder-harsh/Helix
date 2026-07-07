import math
import os
from typing import Any

from helix_platform.spatial.providers import (
    NominatimGeoProvider,
    OverpassPlacesProvider,
)


class SpatialIndex:
    """In-memory spatial index representing geographical points and bound checks.

    [DESIGN NOTE & WARNING]:
    The polygon coordinates mapped below are simplified static placeholders enclosing
    parts of Shivaji Nagar and Central Bengaluru. These serve as structural mock data
    for the hackathon demo visualization and ray-casting tests. In a production
    environment, these boundaries should be dynamically populated by loading official
    municipal ward/constituency GIS boundary datasets (GeoJSON/Shapefiles).
    """

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

        # Determine provider types
        geocoder_type = os.environ.get("GEOCODER_PROVIDER", "nominatim")
        places_type = os.environ.get("PLACES_PROVIDER", "overpass")

        if geocoder_type == "nominatim":
            self.geocoder = NominatimGeoProvider()
        else:
            self.geocoder = None

        if places_type == "overpass":
            self.places_provider = OverpassPlacesProvider()
        else:
            self.places_provider = None

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

    def search_nearby_places(
        self, lat: float, lng: float, radius_m: int, place_type: str
    ) -> list[dict[str, Any]]:
        """Search nearby places using configured PlacesProvider or fallback to mock data."""
        places = []
        if self.places_provider:
            places = self.places_provider.search_places(lat, lng, radius_m, place_type)
        if not places:
            return self._get_mock_places(lat, lng, place_type)
        return places

    def geocode_address(self, address: str) -> dict[str, Any] | None:
        """Geocodes an address to coordinates using configured GeoProvider or fallback."""
        res = None
        if self.geocoder:
            res = self.geocoder.geocode(address)
        if not res:
            return self._get_mock_geocode(address)
        return res

    def reverse_geocode(self, lat: float, lng: float) -> str | None:
        """Reverse geocodes coordinate to address using configured GeoProvider or fallback."""
        address = None
        if self.geocoder:
            address = self.geocoder.reverse_geocode(lat, lng)
        if not address:
            return self._get_mock_reverse_geocode(lat, lng)
        return address

    def _get_mock_places(
        self, _lat: float, _lng: float, place_type: str
    ) -> list[dict[str, Any]]:
        if place_type == "school":
            return [
                {
                    "name": "Shivaji Nagar Government Primary School",
                    "latitude": 12.9780,
                    "longitude": 77.5940,
                    "place_id": "mock-school-1",
                    "address": "Shivaji Nagar Shivaji Road, Bengaluru",
                    "rating": 4.2,
                },
                {
                    "name": "Sector 4 High School Block A",
                    "latitude": 12.9820,
                    "longitude": 77.5900,
                    "place_id": "mock-school-2",
                    "address": "Sector 4 Main Road, Bengaluru",
                    "rating": 4.5,
                },
            ]
        if place_type == "hospital":
            return [
                {
                    "name": "Shivaji Nagar General Hospital",
                    "latitude": 12.9750,
                    "longitude": 77.5960,
                    "place_id": "mock-hospital-1",
                    "address": "Shivaji Nagar Main Road, Bengaluru",
                    "rating": 4.1,
                },
                {
                    "name": "Central Clinic Sector 4",
                    "latitude": 12.9805,
                    "longitude": 77.5920,
                    "place_id": "mock-hospital-2",
                    "address": "Sector 4 Cross Road, Bengaluru",
                    "rating": 4.3,
                },
            ]
        return [
            {
                "name": "Shivaji Nagar Ward 12 Playground",
                "latitude": 12.9765,
                "longitude": 77.5950,
                "place_id": "mock-park-1",
                "address": "Shivaji Nagar Playground St, Bengaluru",
                "rating": 4.4,
            },
            {
                "name": "Sector 4 Civic Park & Open Gym",
                "latitude": 12.9815,
                "longitude": 77.5905,
                "place_id": "mock-park-2",
                "address": "Sector 4 Outer Ring Rd, Bengaluru",
                "rating": 4.0,
            },
        ]

    def _get_mock_geocode(self, address: str) -> dict[str, Any] | None:
        if "sector 4" in address.lower():
            return {
                "latitude": 12.9810,
                "longitude": 77.5910,
                "formatted_address": "Sector 4, Shivaji Nagar, Bengaluru, Karnataka 560001",
            }
        return {
            "latitude": 12.9755,
            "longitude": 77.5955,
            "formatted_address": "Shivaji Nagar, Bengaluru, Karnataka 560051",
        }

    def _get_mock_reverse_geocode(self, lat: float, lng: float) -> str | None:
        if 12.9800 <= lat <= 12.9850 and 77.5900 <= lng <= 77.5950:
            return "Sector 4, Shivaji Nagar, Bengaluru, Karnataka 560001"
        return "Shivaji Nagar, Bengaluru, Karnataka 560051"


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
