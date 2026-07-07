from typing import Any

from .duplicate_detector import DuplicateDetector


class ClusteringEngine:
    """Clusters similar citizen reports to form canonical database incidents."""

    def __init__(self, match_threshold: float = 0.70):
        self.detector = DuplicateDetector()
        self.match_threshold = match_threshold

    def find_best_incident_match(
        self,
        issue: dict[str, Any],
        incidents: list[dict[str, Any]],
        canonical_issues: dict[str, dict[str, Any]],
    ) -> tuple[dict[str, Any] | None, float, dict[str, float] | None]:
        """Finds the existing incident with the highest match confidence above the threshold."""
        best_match = None
        best_conf = 0.0
        best_breakdown = None

        for incident in incidents:
            canon = canonical_issues.get(incident["id"])
            if not canon:
                # If no canonical issue is stored, fall back to comparing against incident properties
                canon = incident

            conf, breakdown = self.detector.calculate_confidence(issue, canon)
            if conf >= self.match_threshold and conf > best_conf:
                best_conf = conf
                best_match = incident
                best_breakdown = breakdown

        return best_match, best_conf, best_breakdown
