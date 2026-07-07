from enum import Enum


class TimelineStage(Enum):
    INTAKE = "Intake & Ingestion"
    AI_REVIEW = "AI Verification & Grounding"
    OFFICER_APPROVAL = "Officer Approval"
    DISPATCH = "Department Dispatch"
    WORK_IN_PROGRESS = "Work In Progress"
    RESOLVED = "Work Completed"
    OUTCOME = "Outcome Recorded & Closed"


# Canonical Event Catalog definition matching domain model and workflow lifecycle
EVENT_CATALOG = {
    "REPORTED": {
        "actor": "Citizen (Mobile App)",
        "actor_type": "citizen",
        "action": "REPORTED",
        "description": "Complaint successfully lodged on the platform.",
        "stage": TimelineStage.INTAKE.value,
        "visibility": ["citizen", "officer", "administrator"],
    },
    "DUPLICATE_SCANNED": {
        "actor": "Duplicate Agent",
        "actor_type": "agent",
        "action": "DUPLICATE_SCANNED",
        "description": "Scan complete. Verified duplicate clusters in regional buffer zone.",
        "stage": TimelineStage.AI_REVIEW.value,
        "visibility": ["officer", "administrator"],
    },
    "CLASSIFIED": {
        "actor": "Classification Agent",
        "actor_type": "agent",
        "action": "CLASSIFIED",
        "description": "Complaint text analyzed and classified under the category '{category}'.",
        "stage": TimelineStage.AI_REVIEW.value,
        "visibility": ["officer", "administrator"],
    },
    "SPATIAL_MAPPED": {
        "actor": "Spatial Engine",
        "actor_type": "system",
        "action": "SPATIAL_MAPPED",
        "description": "Cross-referenced complaint GPS coordinates with regional constituency and ward boundary polygons.",
        "stage": TimelineStage.AI_REVIEW.value,
        "visibility": ["officer", "administrator"],
    },
    "POLICY_GROUNDED": {
        "actor": "Policy Agent",
        "actor_type": "agent",
        "action": "POLICY_GROUNDED",
        "description": "Regulatory checklist verified. Grounded eligibility for matched scheme.",
        "stage": TimelineStage.AI_REVIEW.value,
        "visibility": ["officer", "administrator"],
    },
    "BRIEF_GENERATED": {
        "actor": "Helix AI Decision Engine",
        "actor_type": "system",
        "action": "BRIEF_GENERATED",
        "description": "Executive structured Decision Brief successfully generated and proposed to operations deck.",
        "stage": TimelineStage.AI_REVIEW.value,
        "visibility": ["officer", "administrator"],
    },
    "OFFICER_REVIEWED": {
        "actor": "Officer Suresh Rao",
        "actor_type": "officer",
        "action": "OFFICER_REVIEWED",
        "description": "Officer reviewed Decision Brief recommendations and approved the strategy.",
        "stage": TimelineStage.OFFICER_APPROVAL.value,
        "visibility": ["citizen", "officer", "administrator"],
    },
    "DISPATCHED": {
        "actor": "Municipal Router",
        "actor_type": "system",
        "action": "DISPATCHED",
        "description": "Work order routed and assigned to department.",
        "stage": TimelineStage.DISPATCH.value,
        "visibility": ["citizen", "officer", "administrator"],
    },
    "FIELD_DISPATCHED": {
        "actor": "Municipal Router",
        "actor_type": "system",
        "action": "FIELD_DISPATCHED",
        "description": "Field crew scheduled and dispatched for on-site visit.",
        "stage": TimelineStage.DISPATCH.value,
        "visibility": ["citizen", "officer", "administrator"],
    },
    "WORK_STARTED": {
        "actor": "Field Operations Team",
        "actor_type": "field_crew",
        "action": "WORK_STARTED",
        "description": "Repair crew has arrived on-site. Excavators deployed.",
        "stage": TimelineStage.WORK_IN_PROGRESS.value,
        "visibility": ["citizen", "officer", "administrator"],
    },
    "RESOLVED": {
        "actor": "Resolving Department",
        "actor_type": "department",
        "action": "RESOLVED",
        "description": "Maintenance crew completed restoration works.",
        "stage": TimelineStage.RESOLVED.value,
        "visibility": ["citizen", "officer", "administrator"],
    },
    "VERIFIED": {
        "actor": "Citizen (Mobile App)",
        "actor_type": "citizen",
        "action": "VERIFIED",
        "description": "Citizen verified resolution of the reported issue.",
        "stage": TimelineStage.OUTCOME.value,
        "visibility": ["citizen", "officer", "administrator"],
    },
    "CLOSED": {
        "actor": "Citizen & Outcome Engine",
        "actor_type": "system",
        "action": "CLOSED",
        "description": "Citizen verified resolution. Health score metrics updated.",
        "stage": TimelineStage.OUTCOME.value,
        "visibility": ["citizen", "officer", "administrator"],
    },
    "CLUSTER_CREATED": {
        "actor": "Duplicate Agent",
        "actor_type": "agent",
        "action": "CLUSTER_CREATED",
        "description": "Duplicate Cluster Created and registered in regional buffer zone.",
        "stage": TimelineStage.AI_REVIEW.value,
        "visibility": ["officer", "administrator"],
    },
    "REPORTS_ADDED": {
        "actor": "Duplicate Agent",
        "actor_type": "agent",
        "action": "REPORTS_ADDED",
        "description": "Supporting Citizen Reports mapped and associated with this Incident cluster.",
        "stage": TimelineStage.AI_REVIEW.value,
        "visibility": ["officer", "administrator"],
    },
    "IMPACT_INCREASED": {
        "actor": "Duplicate Agent",
        "actor_type": "agent",
        "action": "IMPACT_INCREASED",
        "description": "Community Impact Increased. Local severity priority score upgraded.",
        "stage": TimelineStage.AI_REVIEW.value,
        "visibility": ["citizen", "officer", "administrator"],
    },
}
