# ruff: noqa: N816
class MockLocation:
    def __init__(self, lat: float, lng: float):
        self.lat = lat
        self.lng = lng


class MockIssue:
    def __init__(
        self,
        id: str,
        title: str,
        description: str,
        category: str,
        lat: float,
        lng: float,
        status: str,
        priority: str,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.category = category
        self.location = MockLocation(lat, lng)
        self.status = status
        self.priority = priority


mockIssues = [
    MockIssue(
        id="ISS-1001",
        title="Potable Water Pipeline Leakage",
        description="Main supply pipeline leaking near Gate 3 of Sector 4 Central Park. Thousands of liters of water being wasted daily.",
        category="Water Supply & Sanitation",
        lat=12.9716,
        lng=77.6412,
        status="In_Progress",
        priority="High",
    ),
    MockIssue(
        id="ISS-1002",
        title="Water Logging at Metro Construction Junction",
        description="Severe water logging under the Metro Pillar 142 junction after last night's rainfall. Traffic is gridlocked.",
        category="Stormwater Drainage",
        lat=12.9421,
        lng=77.5910,
        status="Submitted",
        priority="Critical",
    ),
    MockIssue(
        id="ISS-1003",
        title="Streetlight Outages on Outer Ring Road",
        description="A continuous stretch of 8 streetlights is non-functional, making the highway extremely dangerous for night commuters.",
        category="Public Lighting",
        lat=12.9852,
        lng=77.6724,
        status="Validated",
        priority="Medium",
    ),
    MockIssue(
        id="ISS-1004",
        title="Uncollected Municipal Solid Waste",
        description="Garbage sorting bins have not been cleared for 4 days. Strong odor and stray animals spreading waste.",
        category="Solid Waste Management",
        lat=12.9112,
        lng=77.5621,
        status="Completed",
        priority="Medium",
    ),
    MockIssue(
        id="issue-roads-123",
        title="Potholes in Shivaji Nagar School Zone",
        description="Potholes on Shivaji Road near Shivaji Nagar Primary School.",
        category="Roads & Sidewalks",
        lat=12.9755,
        lng=77.5955,
        status="TRIAGED",
        priority="MEDIUM",
    ),
]
