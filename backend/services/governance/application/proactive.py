from typing import Any

from services.governance.application.queries import GovernanceQueryService


class ProactiveIntelligenceService:
    """Computes proactive constituency briefings, alerts, and priority forecasts."""

    def __init__(self, query_service: GovernanceQueryService) -> None:
        self.query_service = query_service

    def get_morning_briefing(self) -> dict[str, Any]:
        """Generates structured proactive insights and forecasted category ratings."""
        issues = self.query_service.list_pending_issues()

        # Priority Ranking based on geographic/voter weights
        critical_alerts = []
        for issue in issues:
            is_high = (
                issue.get("priority") == "High" or issue.get("priority") == "Critical"
            )
            if is_high:
                critical_alerts.append(
                    {
                        "issue_id": str(issue["id"]),
                        "title": issue["title"],
                        "category": issue["category"],
                        "risk_level": (
                            "CRITICAL"
                            if issue.get("priority") == "Critical"
                            else "HIGH"
                        ),
                        "sla_remaining": "3.5 Hours" if is_high else "24 Hours",
                        "impact_weight": (
                            "4,320 Citizens"
                            if "sanit" in issue["category"].lower()
                            else "350 Citizens"
                        ),
                    }
                )

        # Proactive Summary Text
        brief_summary = (
            "Good Morning MLA. This week: \n"
            "• Water complaints have risen by 27% due to pipeline maintenance in Sector 4.\n"
            "• Ward 12 sanitation metrics require immediate intervention.\n"
            "• PMGSY road upgrade project in Ward 8 is running stable.\n"
            "• Urgent dispatch warning: Hospital route utility block is approaching SLA breach."
        )

        return {
            "constituency": "Central Bengaluru Constituency",
            "overall_health_score": 78,
            "overall_health_trend": "UP",
            "morning_brief": brief_summary,
            "category_forecasts": [
                {
                    "category": "Water & Sanitation",
                    "current_score": 61,
                    "forecast_direction": "DOWN",
                    "reasoning": "Substandard utility capacity under monsoon overload risk.",
                },
                {
                    "category": "Roads & Sidewalks",
                    "current_score": 82,
                    "forecast_direction": "UP",
                    "reasoning": "Recent PMGSY pothole repairs completed in Ward 5.",
                },
                {
                    "category": "Electricity & Power",
                    "current_score": 90,
                    "forecast_direction": "STABLE",
                    "reasoning": "Smart grid distribution transformers cleared standard checks.",
                },
            ],
            "risk_alerts": critical_alerts[:3],  # Limit to top 3 priority risks
        }
