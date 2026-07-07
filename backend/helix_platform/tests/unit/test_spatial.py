from helix_platform.spatial.engine import (
    GeoService,
    IssueClustering,
    SpatialIndex,
)


def test_haversine_distance() -> None:
    # Proximity from Ward 12 Playground to Richmond Road Depot
    # (12.9716, 77.5946) to (12.9750, 77.5990) is ~0.61 km
    distance = GeoService.calculate_distance(12.9716, 77.5946, 12.9750, 77.5990)
    assert 0.5 <= distance <= 0.7


def test_ray_casting_bound_checks() -> None:
    index = SpatialIndex()
    # Center of Shivaji Nagar ward should return True
    inside = index.is_inside_polygon(
        12.9750, 77.5950, index.ward_boundaries["Shivaji Nagar (Ward 12)"]
    )
    assert inside is True

    # Point outside Bangalore Central constituency should return False
    outside = index.is_inside_polygon(
        13.5000, 78.5000, index.constituency_boundaries["Bangalore Central"]
    )
    assert outside is False


def test_geojson_boundary_translation() -> None:
    service = GeoService()
    geojson = service.get_boundaries_as_geojson()
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 2
    assert geojson["features"][0]["geometry"]["type"] == "Polygon"


def test_issue_marker_clustering() -> None:
    issues = [
        {
            "id": "1",
            "title": "Garbage 1",
            "category": "sanitation",
            "latitude": 12.9716,
            "longitude": 77.5946,
        },
        {
            "id": "2",
            "title": "Garbage 2",
            "category": "sanitation",
            "latitude": 12.9720,
            "longitude": 77.5949,
        },  # close
        {
            "id": "3",
            "title": "Pothole 1",
            "category": "roads",
            "latitude": 12.9900,
            "longitude": 77.6500,
        },  # far
    ]
    clusters = IssueClustering.cluster_issues(issues, radius_km=0.5)
    assert len(clusters) == 2  # 1 cluster + 1 single issue

    # Locate the cluster
    cluster = next((c for c in clusters if c["type"] == "cluster"), None)
    assert cluster is not None
    assert cluster["count"] == 2
    assert "1" in cluster["ids"]
    assert "2" in cluster["ids"]


from unittest.mock import patch


def test_search_nearby_places() -> None:
    service = GeoService()
    with patch.object(
        service.places_provider,
        "search_places",
        return_value=[
            {
                "name": "Shivaji Nagar School",
                "latitude": 12.978,
                "longitude": 77.594,
                "place_id": "1",
                "address": "Road",
                "rating": 4.5,
            }
        ],
    ):
        places = service.search_nearby_places(12.9755, 77.5955, 1000, "school")
        assert len(places) > 0
        assert "name" in places[0]
        assert "latitude" in places[0]
        assert "longitude" in places[0]


def test_geocode_address() -> None:
    service = GeoService()
    with patch.object(
        service.geocoder,
        "geocode",
        return_value={
            "latitude": 12.9810,
            "longitude": 77.5910,
            "formatted_address": "Sector 4, Shivaji Nagar, Bengaluru",
        },
    ):
        coords = service.geocode_address("Sector 4, Shivaji Nagar")
        assert coords is not None
        assert coords["latitude"] == 12.9810
        assert coords["longitude"] == 77.5910


def test_reverse_geocode() -> None:
    service = GeoService()
    with patch.object(
        service.geocoder,
        "reverse_geocode",
        return_value="Sector 4, Shivaji Nagar",
    ):
        address = service.reverse_geocode(12.9810, 77.5910)
        assert "Sector 4" in address
