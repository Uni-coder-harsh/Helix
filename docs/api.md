---
owner: "@harsh"
version: "1.0.0"
status: "Published"
last_updated: "2026-07-07"
reviewer: "@harsh"
dependencies: []
---

# API Contract

This document acts as the API specification registry for the microservices in Helix.

## API Standards

- All APIs must follow standard RESTful or gRPC practices.
- JSON payload formats must be validated using OpenAPI schemas.
- Authenticators must use JWT tokens.

## Geo-Intelligence (Spatial) API Endpoints

The Spatial Intelligence service exposes geo-referencing, geocoding, boundary polygons, and Google Places proxy operations.

### 1. Search Nearby Civic Assets (Places Proxy)
* **Endpoint:** `GET /governance/spatial/places`
* **Description:** Queries nearby assets (schools, hospitals, parks) using the OpenStreetMap Overpass API. If the provider is offline, it falls back to realistic localized mock data.
* **Parameters:**
  - `latitude` (float, required): Center latitude.
  - `longitude` (float, required): Center longitude.
  - `radius` (int, optional): Search radius in meters (default: 1500).
  - `type` (str, optional): Place type filters (e.g., `school`, `hospital`, `park`, default: `school`).
* **Response Sample:**
  ```json
  [
    {
      "name": "Shivaji Nagar Government Primary School",
      "latitude": 12.9780,
      "longitude": 77.5940,
      "place_id": "mock-school-1",
      "address": "Shivaji Nagar Shivaji Road, Bengaluru",
      "rating": 4.2
    }
  ]
  ```

### 2. Geocode Address to Coordinates
* **Endpoint:** `GET /governance/spatial/geocode`
* **Description:** Geocodes text addresses to coordinates.
* **Parameters:**
  - `address` (str, required): The query address string.
* **Response Sample:**
  ```json
  {
    "latitude": 12.9810,
    "longitude": 77.5910,
    "formatted_address": "Sector 4, Shivaji Nagar, Bengaluru, Karnataka 560001"
  }
  ```

### 3. Reverse Geocode Coordinates to Address
* **Endpoint:** `GET /governance/spatial/reverse-geocode`
* **Description:** Converts coordinates to a formatted address.
* **Parameters:**
  - `latitude` (float, required): Target latitude.
  - `longitude` (float, required): Target longitude.
* **Response Sample:**
  ```json
  {
    "formatted_address": "Sector 4, Shivaji Nagar, Bengaluru, Karnataka 560001"
  }
  ```

### 4. Filter Issues Geographically (Spatial Query)
* **Endpoint:** `GET /governance/spatial/query`
* **Description:** Query and filter issues by distance radius or bounding box, including logical status or category matching.
* **Parameters:**
  - `lat` / `lng` (float, optional): Coordinates of search center.
  - `radius_km` (float, optional): Great-circle radius to search in.
  - `min_lat` / `min_lng` / `max_lat` / `max_lng` (float, optional): Bounding box coordinates.
  - `category` (str, optional): Filter by issue category.
  - `status` (str, optional): Filter by issue status.
* **Response Sample:**
  ```json
  [
    {
      "id": "complaint-uuid-103",
      "title": "Water Main Leak Shivaji Nagar",
      "latitude": 12.9755,
      "longitude": 77.5955,
      "category": "Water Supply & Sanitation",
      "status": "TRIAGED",
      "priority": "HIGH",
      "distance_km": 0.42
    }
  ]
  ```

## Explainable AI Decision Engine API Endpoints

The Governance service exposes explainable structured Decision Briefs for pending tickets.

### 1. Compile Issue Decision Brief
* **Endpoint:** `GET /governance/issues/{issue_id}/decision-brief`
* **Description:** Compiles and retrieves a structured decision brief containing geographical context, duplicate checks, matched regulatory policies/schemes, alternative option evaluations, and hybrid scoring metrics.
* **Parameters:**
  - `issue_id` (str, required): The target issue ID.
* **Response Sample:**
  ```json
  {
    "problem": {
      "id": "mock-issue-101",
      "title": "Water Leakage near Government School",
      "description": "Large water main leak causing road erosion.",
      "category": "Water Supply & Sanitation",
      "location": {
        "latitude": 12.9755,
        "longitude": 77.5955
      },
      "status": "TRIAGED",
      "priority": "HIGH"
    },
    "evidence": [
      "18 duplicate complaints reported in the immediate coordinate buffer.",
      "Active constituency hotspot status triggered for this georeference coordinate.",
      "2 civic assets located within the buffer impact zone: Ward 12 Playground Garbage Bin Terminal, Govt School Block A."
    ],
    "nearby_assets": [
      {
        "id": "asset-ref-0",
        "name": "Govt School Block A",
        "type": "school",
        "distance_meters": 140
      }
    ],
    "applicable_policies": [
      {
        "name": "Sanitation Waste Management Regulation 2024",
        "code": "REG-2024-09"
      }
    ],
    "applicable_schemes": [
      {
        "name": "Swachh Bharat Abhiyan Subsidy",
        "subsidy_ratio": 0.6
      }
    ],
    "impact_summary": {
      "affected_population": 4320,
      "urgency_score": 0.9,
      "severity_level": "HIGH"
    },
    "alternative_actions": [
      {
        "option_name": "Spot Patch Repair",
        "description": "Localized clearing and temporary segment sealing.",
        "estimated_cost": "₹2.5 Lakhs",
        "sla": "24 Hours",
        "durability": "Low (estimated lifespan < 6 months)",
        "risks": "High risk of recurring leak blockages under high water pressure.",
        "feasibility": "High",
        "is_recommended": false
      },
      {
        "option_name": "Capital Pipeline Trunk Reconstruction",
        "description": "Full replacement of the damaged structural main trunk.",
        "estimated_cost": "₹18.0 Lakhs",
        "sla": "45 Days",
        "durability": "High (estimated lifespan 15+ years)",
        "risks": "Higher budget requirement; requires brief localized traffic detour.",
        "feasibility": "Medium-High",
        "is_recommended": true
      }
    ],
    "recommendation": {
      "suggested_department": "Municipal Sanitation Department",
      "recommended_action": "Dispatch Emergency Sanitation Leak Clearing Crew",
      "estimated_cost": "₹2.5 Lakhs",
      "sla": "24 Hours"
    },
    "reasoning": [
      "Jal Jeevan Mission guidelines suggest complete rebuilds for trunk failures exceeding 15 active tickets.",
      "Proximity to Govt School Block A (within 140m) increases priority to prevent public health hazards."
    ],
    "confidence": 94,
    "follow_up_actions": [
      "Initiate structural design validation for the pipeline trunk.",
      "Notify school administration of the scheduled construction window."
    ]
  }
  ```

### 2. Retrieve Canonical Issue Lifecycle Timeline
* **Endpoint:** `GET /governance/issues/{issue_id}/timeline`
* **Description:** Compiles and retrieves the canonical progress timeline and audit trail for an issue. Entries are dynamically filtered and formatted based on user role-based permissions.
* **Parameters:**
  - `issue_id` (str, required): The target issue ID.
  - `role` (str, optional): User role filter (`citizen`, `officer`, `administrator`, default: `citizen`).
* **Response Sample (role=citizen):**
  ```json
  {
    "issue_id": "mock-issue-101",
    "current_stage": "AI Verification & Grounding",
    "progress": 10,
    "estimated_next_action": "AI multi-agent verification & duplicate mapping scan.",
    "estimated_remaining_sla_hours": 48,
    "timeline": [
      {
        "id": "tl-rep-uuid",
        "timestamp": "2026-07-07T12:00:00Z",
        "actor": "Citizen",
        "actor_type": "citizen",
        "action": "REPORT_SUBMITTED",
        "description": "Your complaint has been successfully registered.",
        "status": "COMPLETED",
        "metadata": {
          "channel": "mobile_app",
          "notification": {
            "type": "SMS",
            "status": "DELIVERED",
            "text": "Helix: Your complaint has been successfully registered."
          }
        }
      },
      {
        "id": "tl-review-citizen-uuid",
        "timestamp": "2026-07-07T12:00:05Z",
        "actor": "Helix Platform",
        "actor_type": "system",
        "action": "UNDER_REVIEW",
        "description": "AI verification scan, duplicate mapping, and policy checks are in progress.",
        "status": "IN_PROGRESS",
        "metadata": {
          "agents_active": ["ClassificationAgent", "DuplicateAgent", "SpatialAgent", "PolicyAgent"]
        }
      }
    ]
  }
  ```

## Evidence Intelligence & Duplicate Clustering API Endpoints

The Governance service exposes evidence clustering and duplicate report mapping operations.

### 1. Search Duplicate Complaints
* **Endpoint:** `GET /governance/issues/{issue_id}/duplicates`
* **Description:** Identifies potential duplicate citizen reports matching this issue's coordinates, text contents, and timing threshold window.
* **Parameters:**
  - `issue_id` (str, required): The target issue ID to match against.
* **Response Sample:**
  ```json
  [
    {
      "issue": {
        "id": "mock-uuid-2",
        "title": "Water leakage and flooding",
        "category": "Water Supply & Sanitation",
        "latitude": 12.9758,
        "longitude": 77.5957
      },
      "confidence": 0.767,
      "breakdown": {
        "spatial": 0.9,
        "text": 0.81,
        "temporal": 0.98,
        "category": 1.0,
        "distance_meters": 33.0,
        "time_diff_days": 0.08
      },
      "already_merged": false
    }
  ]
  ```

### 2. List Clustered Incidents
* **Endpoint:** `GET /governance/incidents`
* **Description:** Returns all grouped incident clusters.
* **Response Sample:**
  ```json
  [
    {
      "id": "inc-uuid-1",
      "title": "Incident Cluster: Water Main Leak Shivaji Nagar",
      "category": "Water Supply & Sanitation",
      "status": "TRIAGED",
      "reports_count": 3
    }
  ]
  ```

### 3. Retrieve Incident Details
* **Endpoint:** `GET /governance/incidents/{incident_id}`
* **Description:** Retrieves incident metadata along with all associated child issues (citizen reports).
* **Parameters:**
  - `incident_id` (str, required): The incident ID.
* **Response Sample:**
  ```json
  {
    "id": "inc-uuid-1",
    "title": "Incident Cluster: Water Main Leak Shivaji Nagar",
    "category": "Water Supply & Sanitation",
    "status": "TRIAGED",
    "reports_count": 2,
    "reports": [
      {
        "id": "issue-1",
        "title": "Water Main Leak near Shivaji School",
        "description": "Large water main leak causing road erosion."
      },
      {
        "id": "issue-2",
        "title": "Water leaking",
        "description": "Pipelake leak on Shivaji Road."
      }
    ]
  }
  ```

### 4. Merge Issue into Incident
* **Endpoint:** `POST /governance/incidents/{incident_id}/merge`
* **Description:** Merges a citizen issue report into an incident cluster.
* **Request Body:**
  ```json
  {
    "issue_id": "issue-uuid-to-merge"
  }
  ```
* **Response Sample:**
  ```json
  {
    "success": true,
    "issue_id": "issue-uuid-to-merge",
    "incident_id": "inc-uuid-1",
    "reports_count": 3
  }
  ```
