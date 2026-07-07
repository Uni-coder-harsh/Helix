from typing import Any


class AlternativesEvaluator:
    """Evaluates option matrices comparing cost, SLA, risks, and resolution strategies."""

    @staticmethod
    def get_alternatives(
        category: str,  # noqa: ARG004
        issue_description: str,
    ) -> list[dict[str, Any]]:
        desc = issue_description.lower()
        is_sanit = (
            "water" in desc or "leak" in desc or "drain" in desc or "sanit" in desc
        )

        if is_sanit:
            return [
                {
                    "option_name": "Spot Patch Repair",
                    "description": "Localized clearing and temporary segment sealing.",
                    "estimated_cost": "₹2.5 Lakhs",
                    "sla": "24 Hours",
                    "durability": "Low (estimated lifespan < 6 months)",
                    "risks": "High risk of recurring leak blockages under high water pressure.",
                    "feasibility": "High",
                    "is_recommended": False,
                    "confidence": 75,
                    "expected_impact": "Medium-Low",
                },
                {
                    "option_name": "Capital Pipeline Trunk Reconstruction",
                    "description": "Full replacement of the damaged structural main trunk.",
                    "estimated_cost": "₹18.0 Lakhs",
                    "sla": "45 Days",
                    "durability": "High (estimated lifespan 15+ years)",
                    "risks": "Higher budget requirement; requires brief localized traffic detour.",
                    "feasibility": "Medium-High",
                    "is_recommended": True,
                    "confidence": 95,
                    "expected_impact": "High",
                },
                {
                    "option_name": "Monitor and Defer Action",
                    "description": "Add to monthly oversight log and deploy warning barriers.",
                    "estimated_cost": "₹0.2 Lakhs",
                    "sla": "90 Days",
                    "durability": "None",
                    "risks": "Likely to trigger increased public complaints and local flooding.",
                    "feasibility": "High",
                    "is_recommended": False,
                    "confidence": 30,
                    "expected_impact": "Low",
                },
            ]
        return [
            {
                "option_name": "Pothole Cold-Mix Patching",
                "description": "Deploy cold-mix asphalt to fill potholes immediately.",
                "estimated_cost": "₹1.8 Lakhs",
                "sla": "48 Hours",
                "durability": "Low-Medium (estimated lifespan < 1 year)",
                "risks": "Monsoon washouts likely to strip patch repairs quickly.",
                "feasibility": "High",
                "is_recommended": False,
                "confidence": 80,
                "expected_impact": "Medium",
            },
            {
                "option_name": "Full Corridor Road Overlay & drainage",
                "description": "Milling and paving of the entire street segment with concrete overlay.",
                "estimated_cost": "₹12.0 Lakhs",
                "sla": "30 Days",
                "durability": "High (estimated lifespan 10+ years)",
                "risks": "Higher capital budget; temporary disruption to pedestrian zones.",
                "feasibility": "Medium-High",
                "is_recommended": True,
                "confidence": 94,
                "expected_impact": "High",
            },
            {
                "option_name": "Observation list",
                "description": "Place under ongoing observation pending next budget cycle.",
                "estimated_cost": "₹0",
                "sla": "120 Days",
                "durability": "None",
                "risks": "Escalating road safety hazards and pedestrian claims.",
                "feasibility": "High",
                "is_recommended": False,
                "confidence": 40,
                "expected_impact": "Low",
            },
        ]
