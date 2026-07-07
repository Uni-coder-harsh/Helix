import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from helix_platform.security import create_access_token
from services.main import app


@pytest.mark.asyncio
async def test_complete_vertical_slice() -> None:
    """Verifies the complete end-to-end P0 vertical slice with RBAC checks.

    Citizen Submit -> Auto Triage -> AI Rec -> Officer Review -> Accept.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 1. POST issue (Citizen submission)
        payload = {
            "citizen_id": "00000000-0000-0000-0000-000000000000",
            "title": "Overflowing Garbage Bin",
            "description": "The public garbage bin in front of Ward 12 playground is overflowing with trash.",
            "category": "sanitation",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "formatted_address": "Ward 12 Playground Entrance",
        }
        # Citizen role is required to submit issues
        response = await client.post(
            "/governance/issues", json=payload, headers={"X-User-Role": "Citizen"}
        )
        assert response.status_code == 200
        issue_id = response.json()["issue_id"]
        assert issue_id is not None
        assert response.json()["status"] == "INTAKE"

        # 2. Wait for EventBus background tasks to propagate and complete
        await asyncio.sleep(0.5)

        # 3. GET pending issues (Officer dashboard load)
        # Officer role is required to view pending issues
        response = await client.get(
            "/governance/issues/pending", headers={"X-User-Role": "Officer"}
        )
        assert response.status_code == 200
        pending_list = response.json()
        assert len(pending_list) > 0

        # Find the submitted issue
        issue_item = next(
            (item for item in pending_list if item["id"] == issue_id), None
        )
        assert issue_item is not None
        assert issue_item["status"] == "TRIAGED"
        assert issue_item["priority"] == "HIGH"
        assert issue_item["has_recommendation"] is True
        recommendation_id = issue_item["recommendation_id"]
        assert recommendation_id is not None

        # 4. GET AI recommendation details (Officer role)
        response = await client.get(
            f"/governance/recommendations/{issue_id}",
            headers={"X-User-Role": "Officer"},
        )
        assert response.status_code == 200
        rec_data = response.json()
        assert rec_data["id"] == recommendation_id
        assert rec_data["suggested_category"] == "sanitation"
        assert rec_data["status"] == "PROPOSED"
        assert "standard SLA" in rec_data["rationale"]

        # 4b. GET issue decision context (Officer role)
        response = await client.get(
            f"/governance/issues/{issue_id}/context",
            headers={"X-User-Role": "Officer"},
        )
        assert response.status_code == 200
        ctx_data = response.json()
        assert ctx_data["priority"] == "HIGH"
        assert ctx_data["suggested_department"] == "Municipal Sanitation Department"
        assert len(ctx_data["supporting_evidence"]) > 0

        # 5. POST accept recommendation (Officer action)
        response = await client.post(
            f"/governance/recommendations/{recommendation_id}/accept",
            headers={"X-User-Role": "Officer"},
        )
        assert response.status_code == 200
        accept_data = response.json()
        assert accept_data["status"] == "SUCCESS"
        assert accept_data["new_issue_status"] == "ASSIGNED"

        # 6. GET dashboard stats (Officer role)
        response = await client.get(
            "/governance/dashboard/stats", headers={"X-User-Role": "Officer"}
        )
        assert response.status_code == 200
        stats = response.json()
        assert stats["APPROVED"] == 1
        assert stats["PENDING"] == 0


@pytest.mark.asyncio
async def test_spatial_endpoints() -> None:
    """Verifies that the new GIS proxy and query endpoints function correctly with role headers."""
    from unittest.mock import patch

    with (
        patch(
            "helix_platform.spatial.providers.NominatimGeoProvider.geocode"
        ) as mock_geocode,
        patch(
            "helix_platform.spatial.providers.NominatimGeoProvider.reverse_geocode"
        ) as mock_reverse,
        patch(
            "helix_platform.spatial.providers.OverpassPlacesProvider.search_places"
        ) as mock_places,
    ):
        mock_geocode.return_value = {
            "latitude": 12.9810,
            "longitude": 77.5910,
            "formatted_address": "Sector 4, Shivaji Nagar, Bengaluru, Karnataka 560001",
        }
        mock_reverse.return_value = (
            "Sector 4, Shivaji Nagar, Bengaluru, Karnataka 560001"
        )
        mock_places.return_value = [
            {
                "name": "Shivaji Nagar School",
                "latitude": 12.978,
                "longitude": 77.594,
                "place_id": "osm-123",
                "address": "Road",
                "rating": 4.5,
            }
        ]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # 1. Test places search proxy (requires spatial:read)
            response = await client.get(
                "/governance/spatial/places?latitude=12.9755&longitude=77.5955&type=school",
                headers={"X-User-Role": "Citizen"},
            )
            assert response.status_code == 200
            places = response.json()
            assert len(places) > 0
            assert "name" in places[0]

            # 2. Test Geocoding proxy
            response = await client.get(
                "/governance/spatial/geocode?address=Sector 4, Shivaji Nagar",
                headers={"X-User-Role": "Citizen"},
            )
            assert response.status_code == 200
            coords = response.json()
            assert coords["latitude"] == 12.9810
            assert coords["longitude"] == 77.5910

            # 3. Test Reverse Geocoding proxy
            response = await client.get(
                "/governance/spatial/reverse-geocode?latitude=12.9810&longitude=77.5910",
                headers={"X-User-Role": "Citizen"},
            )
            assert response.status_code == 200
            addr = response.json()
            assert "Sector 4" in addr["formatted_address"]

            # 4. Test spatial query issue search
            response = await client.get(
                "/governance/spatial/query?lat=12.9755&lng=77.5955&radius_km=5.0",
                headers={"X-User-Role": "Citizen"},
            )
            assert response.status_code == 200
            issues = response.json()
            assert isinstance(issues, list)


@pytest.mark.asyncio
async def test_timeline_and_brief_download_endpoints() -> None:
    """Verifies that the timeline endpoint and brief download endpoints respond correctly with role headers."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        issue_id = "issue-roads-123"

        # 1. GET Timeline (Citizen role)
        response = await client.get(
            f"/governance/issues/{issue_id}/timeline?role=citizen",
            headers={"X-User-Role": "Citizen"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["issue_id"] == issue_id
        assert data["progress"] > 0
        assert len(data["timeline"]) > 0

        # 2. GET Timeline (Officer role)
        response_off = await client.get(
            f"/governance/issues/{issue_id}/timeline?role=officer",
            headers={"X-User-Role": "Officer"},
        )
        assert response_off.status_code == 200
        data_off = response_off.json()
        assert len(data_off["timeline"]) >= len(data["timeline"])

        # 3. GET Decision Brief HTML download (requires brief:read)
        response_dl = await client.get(
            f"/governance/issues/{issue_id}/decision-brief/download",
            headers={"X-User-Role": "Officer"},
        )
        assert response_dl.status_code == 200
        assert "text/html" in response_dl.headers["content-type"]
        assert "Helix Decision Brief" in response_dl.text


@pytest.mark.asyncio
async def test_unauthenticated_requests_fail() -> None:
    """Verifies that requests without credentials yield a 401 Unauthorized status."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Request pending issues without role or token
        response = await client.get("/governance/issues/pending")
        assert response.status_code == 401
        assert "missing or invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_unauthorized_permissions_fail() -> None:
    """Verifies that a role without the required permission yields a 403 Forbidden status."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Citizen attempting to retrieve pending officer issues
        response = await client.get(
            "/governance/issues/pending", headers={"X-User-Role": "Citizen"}
        )
        assert response.status_code == 403
        assert "permission denied" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_token_based_authorization() -> None:
    """Verifies that a signed JWT token correctly authenticates and grants access."""
    # Generate a cryptographically signed token for Officer
    token_payload = {"role": "Officer", "sub": "officer-uuid-123"}
    token = create_access_token(token_payload)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/governance/issues/pending",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role_name,expected_status",
    [
        ("System Administrator", 200),
        ("Platform Administrator", 200),
        ("MLA", 200),
        ("MP", 200),
        ("Officer", 200),
        ("Auditor", 200),
        ("Citizen", 403),
        ("Field Engineer", 403),
    ],
)
async def test_role_based_routing_permissions(
    role_name: str, expected_status: int
) -> None:
    """Verifies permissions matrix across all supported roles for list_pending_issues."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/governance/issues/pending", headers={"X-User-Role": role_name}
        )
        assert response.status_code == expected_status
