import datetime
from typing import Any

from .similarity import calculate_haversine_distance, calculate_text_similarity


class DuplicateDetector:
    """Computes duplicate similarity scores and confidence percentages."""

    def __init__(
        self,
        spatial_threshold_meters: float = 300.0,
        temporal_threshold_days: float = 30.0,
        weights: dict[str, float] | None = None,
    ):
        self.spatial_threshold = spatial_threshold_meters
        self.temporal_threshold = temporal_threshold_days
        self.weights = weights or {
            "spatial": 0.40,
            "text": 0.35,
            "temporal": 0.15,
            "category": 0.10,
        }

    def calculate_similarity_breakdown(
        self, issue1: dict[str, Any], issue2: dict[str, Any]
    ) -> dict[str, float]:
        # Spatial Distance Score
        lat1, lon1 = issue1.get("latitude", 0.0), issue1.get("longitude", 0.0)
        lat2, lon2 = issue2.get("latitude", 0.0), issue2.get("longitude", 0.0)
        dist = calculate_haversine_distance(lat1, lon1, lat2, lon2)
        spatial_score = 1.0 - min(dist / self.spatial_threshold, 1.0)

        # Text Similarity Score (Title + Description)
        text1 = f"{issue1.get('title', '')} {issue1.get('description', '')}"
        text2 = f"{issue2.get('title', '')} {issue2.get('description', '')}"
        text_score = calculate_text_similarity(text1, text2)

        # Temporal Window Score
        t1 = issue1.get("created_at") or datetime.datetime.now(datetime.UTC)
        t2 = issue2.get("created_at") or datetime.datetime.now(datetime.UTC)

        if isinstance(t1, str):
            t1 = datetime.datetime.fromisoformat(t1.replace("Z", "+00:00"))
        if isinstance(t2, str):
            t2 = datetime.datetime.fromisoformat(t2.replace("Z", "+00:00"))

        if t1.tzinfo is None:
            t1 = t1.replace(tzinfo=datetime.UTC)
        if t2.tzinfo is None:
            t2 = t2.replace(tzinfo=datetime.UTC)

        time_diff_days = abs((t1 - t2).total_seconds()) / 86400.0
        temporal_score = 1.0 - min(time_diff_days / self.temporal_threshold, 1.0)

        # Exact Category Match Score
        cat1 = str(issue1.get("category", "")).lower().strip()
        cat2 = str(issue2.get("category", "")).lower().strip()
        category_score = 1.0 if cat1 == cat2 else 0.0

        return {
            "spatial": spatial_score,
            "text": text_score,
            "temporal": temporal_score,
            "category": category_score,
            "distance_meters": dist,
            "time_diff_days": time_diff_days,
        }

    def calculate_confidence(
        self, issue1: dict[str, Any], issue2: dict[str, Any]
    ) -> tuple[float, dict[str, float]]:
        breakdown = self.calculate_similarity_breakdown(issue1, issue2)

        overall = (
            breakdown["spatial"] * self.weights["spatial"]
            + breakdown["text"] * self.weights["text"]
            + breakdown["temporal"] * self.weights["temporal"]
            + breakdown["category"] * self.weights["category"]
        )
        return float(overall), breakdown
