import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from services.main import app


@pytest.mark.asyncio
async def test_complete_vertical_slice() -> None:
    """Verifies the complete end-to-end P0 vertical slice.

    Citizen Submit -> Auto Triage -> AI Rec -> Officer Review -> Accept.
    """
    # Use httpx AsyncClient to run inside the active pytest event loop
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
        response = await client.post("/governance/issues", json=payload)
        assert response.status_code == 200
        issue_id = response.json()["issue_id"]
        assert issue_id is not None
        assert response.json()["status"] == "INTAKE"

        # 2. Wait for EventBus background tasks to propagate and complete
        # (IssueIngestedEvent -> handle_issue_ingested -> IssueTriagedEvent -> handle_issue_triaged)
        await asyncio.sleep(0.5)

        # 3. GET pending issues (Officer dashboard load)
        response = await client.get("/governance/issues/pending")
        assert response.status_code == 200
        pending_list = response.json()
        assert len(pending_list) > 0

        # Find the submitted issue
        issue_item = next(
            (item for item in pending_list if item["id"] == issue_id), None
        )
        assert issue_item is not None
        assert issue_item["status"] == "TRIAGE"
        assert issue_item["priority"] == "HIGH"  # Triage logic maps sanitation to HIGH
        assert issue_item["has_recommendation"] is True
        recommendation_id = issue_item["recommendation_id"]
        assert recommendation_id is not None

        # 4. GET AI recommendation details
        response = await client.get(f"/governance/recommendations/{issue_id}")
        assert response.status_code == 200
        rec_data = response.json()
        assert rec_data["id"] == recommendation_id
        assert rec_data["suggested_category"] == "sanitation"
        assert rec_data["status"] == "PROPOSED"
        assert "Standard resolution timeline" in rec_data["rationale"]

        # 5. POST accept recommendation (Officer action)
        response = await client.post(
            f"/governance/recommendations/{recommendation_id}/accept"
        )
        assert response.status_code == 200
        accept_data = response.json()
        assert accept_data["status"] == "SUCCESS"
        assert accept_data["new_issue_status"] == "ASSIGNED"

        # 6. GET dashboard stats (verifies outcomes updates)
        response = await client.get("/governance/dashboard/stats")
        assert response.status_code == 200
        stats = response.json()
        assert stats["APPROVED"] == 1
        assert stats["PENDING"] == 0
