# ruff: noqa: E501
import datetime
import random
import sys
import uuid
from pathlib import Path

# Adjust path to import from backend workspace
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from helix_platform.persistence import Base, SessionLocal, engine
from services.governance.infrastructure.models import (
    IncidentDB,
    IssueDB,
    RecommendationDB,
)

# Realistic Templates for Bangalore Shivaji Nagar Constituency
TEMPLATES = {
    "water_sanitation": [
        (
            "Potable Water Pipeline Leakage",
            "Main supply pipeline leaking near Shivaji Nagar Shivaji Road. Thousands of liters of drinking water being wasted daily.",
        ),
        (
            "Sewage Overflow on Main Road",
            "Open sewer overflowing near Commercial Street junction. Creating health hazard and foul smell.",
        ),
        (
            "Contaminated Tap Water Supply",
            "Residents of Ward 12 reporting muddy and foul-smelling tap water since last two days.",
        ),
        (
            "Broken Water Meter & Leak",
            "Water meter cracked and spraying water onto the footpath near Shivaji Road.",
        ),
        (
            "No Water Supply in Blocks",
            "Complete disruption of water supply in Shivaji Nagar Block C for 36 hours without notice.",
        ),
    ],
    "roads": [
        (
            "Deep Pothole Shivaji Road",
            "Massive pothole in Shivaji Road causing multiple minor bike accidents daily.",
        ),
        (
            "Broken Sidewalk Slabs",
            "Footpath pavement slabs broken and loose near Shivaji Nagar Metro station, making it dangerous for pedestrians.",
        ),
        (
            "Unpaved Stretch on Cross Road",
            "Road dug up for utility cables months ago has not been asphalted, causing dust clouds.",
        ),
        (
            "Caved-in Road Section",
            "A section of the road has collapsed near Shivaji Nagar bus stand after heavy rain.",
        ),
        (
            "Missing Manhole Cover on Footpath",
            "Open manhole on Shivaji Nagar main footpath. Extremely dangerous for night walkers.",
        ),
    ],
    "drainage": [
        (
            "Stormwater Drain Blockage",
            "Heavy silt and garbage choking the main stormwater drain near Shivaji Nagar Market, causing minor flooding.",
        ),
        (
            "Water Logging under Underpass",
            "Shivaji Nagar Metro bridge underpass flooded with 2 feet of water, stalling traffic.",
        ),
        (
            "Collapsed Stormwater Drain Wall",
            "Slab wall of the primary storm drain collapsed near Shivaji Nagar Ward Office.",
        ),
        (
            "Blocked Roadside Gullies",
            "Rainwater outlets along Shivaji Road blocked with plastic waste, causing water to pool on the street.",
        ),
    ],
    "waste": [
        (
            "Uncollected Municipal Solid Waste",
            "Garbage bins overflowing on Shivaji Road for 4 days. Foul smell and stray dogs.",
        ),
        (
            "Illegal Dumping on Footpath",
            "Construction debris and plastic bags dumped overnight at Shivaji Nagar Sector B corner.",
        ),
        (
            "Commercial Waste Discarded on Street",
            "Food waste from restaurants dumped directly on Shivaji Road lanes, attracting rodents.",
        ),
        (
            "Public Bins Damaged and Broken",
            "Green and blue dry/wet waste municipal bins broken and tipped over near Shivaji Nagar Park.",
        ),
    ],
    "lighting": [
        (
            "Streetlight Outages on Shivaji Road",
            "A continuous stretch of 8 streetlights is non-functional, making the lane pitch black at night.",
        ),
        (
            "Flickering Streetlight in Lane 4",
            "Streetlight blinking continuously, causing distraction and security concerns.",
        ),
        (
            "Exposed Live Wiring on Electric Pole",
            "Broken junction box with live wire exposed on electric pole near Shivaji Nagar Shivaji Road.",
        ),
        (
            "New Streetlight Needed in Shivaji Park",
            "Shivaji Nagar main park has no operational lighting in the children's play area.",
        ),
    ],
}

DEPARTMENTS = {
    "water_sanitation": "Municipal Sanitation Department",
    "roads": "Public Works Department",
    "drainage": "Stormwater Drainage Division",
    "waste": "Solid Waste Management Division",
    "lighting": "BBMP Streetlight & Electrical Division",
}

ADDRESSES = [
    "Shivaji Road, Shivaji Nagar",
    "Sector B, Shivaji Nagar",
    "Junction 3, Shivaji Nagar",
    "Metro Station Corridor, Shivaji Nagar",
    "Commercial Street Area, Shivaji Nagar",
    "Sector 4, Shivaji Nagar",
    "Shivaji Nagar Bus Stand Lane",
    " Shivaji Park Outer Road",
    "Shivaji Nagar Market Cross Road",
    "Ward 12 Residential Zone",
]


def seed_db() -> None:
    # 1. Initialize tables if they do not exist
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Clear existing data to ensure idempotent seeding
    print("Purging existing records...")
    db.query(RecommendationDB).delete()
    db.query(IssueDB).delete()
    db.query(IncidentDB).delete()
    db.commit()

    print("Generating demo dataset (350 issues)...")

    # Define 15 parent incident clusters to simulate duplicates
    incidents = []
    for i in range(15):
        category = random.choice(list(TEMPLATES.keys()))
        title_tpl, desc_tpl = random.choice(TEMPLATES[category])
        lat = random.uniform(12.965, 12.985)
        lon = random.uniform(77.585, 77.615)
        address = random.choice(ADDRESSES)

        inc = IncidentDB(
            id=str(uuid.uuid4()),
            title=f"Incident Cluster: {title_tpl} (Group {i+1})",
            description=f"Consolidated duplicate cluster representing multiple reports of: {desc_tpl}",
            category=category,
            status=random.choice(["TRIAGED", "IN_PROGRESS", "RESOLVED"]),
            latitude=lat,
            longitude=lon,
            location_address=address,
            created_at=datetime.datetime.now(datetime.UTC)
            - datetime.timedelta(days=random.randint(5, 20)),
        )
        db.add(inc)
        incidents.append(inc)

    db.commit()

    # Generate 350 issues
    issues_to_create = []
    recommendations_to_create = []

    for idx in range(350):
        # 40% chance of being linked to an existing incident cluster (a duplicate)
        is_duplicate = random.random() < 0.40
        citizen_id = str(uuid.uuid4())

        if is_duplicate:
            parent_inc = random.choice(incidents)
            category = parent_inc.category
            title_tpl, desc_tpl = random.choice(TEMPLATES[category])
            # Coordinates are offset slightly from the parent incident centroid
            lat = float(parent_inc.latitude) + random.uniform(-0.0008, 0.0008)
            lon = float(parent_inc.longitude) + random.uniform(-0.0008, 0.0008)
            address = parent_inc.location_address
            incident_id = parent_inc.id
            status = parent_inc.status
        else:
            category = random.choice(list(TEMPLATES.keys()))
            title_tpl, desc_tpl = random.choice(TEMPLATES[category])
            lat = random.uniform(12.960, 12.988)
            lon = random.uniform(77.580, 77.618)
            address = random.choice(ADDRESSES)
            incident_id = None
            # Probability-based status distribution
            status_rand = random.random()
            if status_rand < 0.4:
                status = "INTAKE"
            elif status_rand < 0.7:
                status = "TRIAGED"
            elif status_rand < 0.9:
                status = "IN_PROGRESS"
            else:
                status = "RESOLVED"

        priority = random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        issue_id = str(uuid.uuid4())
        created_days_ago = random.randint(1, 30)
        created_at = datetime.datetime.now(datetime.UTC) - datetime.timedelta(
            days=created_days_ago,
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )

        issue = IssueDB(
            id=issue_id,
            citizen_id=citizen_id,
            title=f"{title_tpl} #{1000 + idx}",
            description=f"{desc_tpl} Citizen report submitted via operations terminal.",
            category=category,
            status=status,
            priority=priority,
            location_address=address,
            latitude=lat,
            longitude=lon,
            incident_id=incident_id,
            created_at=created_at,
        )
        issues_to_create.append(issue)

        # Create corresponding AI Recommendation
        suggested_dept = DEPARTMENTS[category]
        confidence = round(random.uniform(84.5, 98.7), 2)
        rec_status = (
            "ACCEPTED"
            if status in ["IN_PROGRESS", "RESOLVED", "CLOSED"]
            else "PROPOSED"
        )
        rationale = (
            f"The reported issue was analyzed via GIS proximity mapping. Proximity scans "
            f"within a 350-meter radius confirm similar reports matching category '{category}'. "
            f"Applying BBMP municipal code and routing guidelines, recommending dispatch to {suggested_dept}."
        )

        rec = RecommendationDB(
            id=str(uuid.uuid4()),
            issue_id=issue_id,
            suggested_category=category,
            suggested_department=suggested_dept,
            confidence_score=confidence,
            rationale=rationale,
            status=rec_status,
            created_at=created_at + datetime.timedelta(seconds=random.randint(10, 45)),
        )
        recommendations_to_create.append(rec)

    # Bulk insert
    print(f"Bulk inserting {len(issues_to_create)} issues...")
    db.add_all(issues_to_create)
    db.commit()

    print(f"Bulk inserting {len(recommendations_to_create)} recommendations...")
    db.add_all(recommendations_to_create)
    db.commit()

    db.close()
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    seed_db()
