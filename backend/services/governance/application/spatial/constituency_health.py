from typing import Any


class ConstituencyHealthEngine:
    """Derives category health scores based on pending issues count and priority weights."""

    @staticmethod
    def calculate_health_scores(issues: list[dict[str, Any]]) -> dict[str, Any]:
        # Initial scores
        scores = {
            "Roads & Sidewalks": 100,
            "Water Supply & Sanitation": 100,
            "Electricity & Power": 100,
            "Healthcare Facilities": 100,
            "Education & Schools": 100,
        }

        # Subtractions based on active issue weights
        for issue in issues:
            category = issue["category"]
            priority = issue.get("priority", "Low")

            # Map category name to standard scoring keys
            matched_key = None
            for key in scores:
                if key.lower() in category.lower() or category.lower() in key.lower():
                    matched_key = key
                    break

            if matched_key:
                weight = 1
                if priority in ["Critical", "High", "HIGH", "CRITICAL"]:
                    weight = 5
                elif priority in ["Medium", "MEDIUM"]:
                    weight = 3

                scores[matched_key] -= weight

        # Enforce bounding floor limits (e.g. min 40)
        for key in scores:
            scores[key] = max(40, scores[key])

        # Overall average score
        avg_score = int(sum(scores.values()) / len(scores))

        return {
            "overall_health_score": avg_score,
            "overall_health_trend": "UP",
            "category_scores": scores,
        }
