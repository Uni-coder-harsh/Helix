from typing import Any


class TimelineFormatter:
    """Formats and filters timeline events based on role-based visibility rules."""

    @staticmethod
    def format_timeline(
        entries: list[dict[str, Any]], role: str
    ) -> list[dict[str, Any]]:
        # Extract duplicate count if present
        duplicates_count = 0
        for entry in entries:
            if entry.get("action") == "DUPLICATE_SCANNED":
                duplicates_count = entry.get("metadata", {}).get("duplicates_found", 0)
                break

        filtered = []
        for entry in entries:
            visibilities = entry.get("visibility", ["officer", "administrator"])

            # Filter by role visibility
            if role != "administrator" and role not in visibilities:
                continue

            # Copy event dictionary
            formatted_entry = {
                "id": entry.get("id"),
                "timestamp": entry.get("timestamp"),
                "actor": entry.get("actor"),
                "actor_type": entry.get("actor_type"),
                "action": entry.get("action"),
                "description": entry.get("description"),
                "status": entry.get("status"),
                "metadata": entry.get("metadata", {}),
            }

            # Map citizen-friendly names to public stages
            if role == "citizen":
                action = entry.get("action")
                if action == "REPORTED":
                    formatted_entry["action"] = "REPORT_SUBMITTED"
                    formatted_entry["actor"] = "Citizen"
                    if duplicates_count > 0:
                        formatted_entry["description"] = (
                            f"This issue is already affecting your community. "
                            f"{duplicates_count} similar reports detected. "
                            f"Your report strengthens the case."
                        )
                    else:
                        formatted_entry["description"] = (
                            "Your complaint has been successfully registered."
                        )
                elif action == "UNDER_REVIEW":
                    formatted_entry["action"] = "UNDER_REVIEW"
                    formatted_entry["actor"] = "Helix Platform"
                    formatted_entry["description"] = (
                        "AI verification scan, duplicate mapping, and policy checks are in progress."
                    )
                elif action == "OFFICER_REVIEWED":
                    # Hide internal officer details or frame citizen-friendly
                    formatted_entry["action"] = "UNDER_REVIEW"
                    formatted_entry["actor"] = "Review Officer"
                    formatted_entry["description"] = (
                        "AI recommendation brief is being reviewed by city officials."
                    )
                elif action == "DISPATCHED":
                    formatted_entry["action"] = "DEPARTMENT_ASSIGNED"
                    formatted_entry["actor"] = "Department Dispatch"
                    dept = entry.get("metadata", {}).get(
                        "department", "Assigned Department"
                    )
                    formatted_entry["description"] = (
                        f"Task assigned to {dept} for execution."
                    )
                elif action == "FIELD_DISPATCHED":
                    # Hide detailed field dispatch or frame as WIP prep
                    continue
                elif action == "WORK_STARTED":
                    formatted_entry["action"] = "WORK_IN_PROGRESS"
                    formatted_entry["actor"] = "Field Crew"
                    formatted_entry["description"] = (
                        "Field team has arrived on-site and repair work is underway."
                    )
                elif action == "RESOLVED":
                    formatted_entry["action"] = "COMPLETED"
                    formatted_entry["actor"] = "Maintenance Division"
                    formatted_entry["description"] = (
                        "Repair work completed. Segment pavement and utility checks passed."
                    )
                elif action == "CLOSED" or action == "VERIFIED":
                    formatted_entry["action"] = "FEEDBACK_REQUESTED"
                    formatted_entry["actor"] = "Citizen Relations"
                    formatted_entry["description"] = (
                        "Awaiting citizen satisfaction review and closeout confirmation."
                    )
                elif action == "IMPACT_INCREASED":
                    formatted_entry["action"] = "COMMUNITY_IMPACT_INCREASED"
                    formatted_entry["actor"] = "Helix Platform"
                    formatted_entry["description"] = (
                        "Multiple reports received. This issue has been prioritized as a community hotspot."
                    )

            filtered.append(formatted_entry)

        return filtered
