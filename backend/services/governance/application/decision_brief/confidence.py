from typing import Any


class ConfidenceScorer:
    """Computes a hybrid confidence rating combining deterministic signals and LLM outputs."""

    @staticmethod
    def compute_confidence(
        context: dict[str, Any], llm_confidence: float | None = None
    ) -> dict[str, Any]:
        signals = {
            "duplicates": 5,
            "policy_match": 5,
            "spatial": 10,
            "historical_similarity": 5,
            "llm": 8,
        }

        # 1. Duplicates Density signal (max 25 pts)
        dup_count = context.get("duplicate_count", 0)
        if dup_count > 10:
            signals["duplicates"] = 25
        elif dup_count > 0:
            signals["duplicates"] = 15

        # 2. Policy/Subsidies matched signal (max 25 pts)
        if context.get("matched_policy") or context.get("matched_scheme"):
            signals["policy_match"] = 25

        # 3. Proximity target safety risk index (max 25 pts)
        assets = context.get("nearby_assets", [])
        if assets:
            signals["spatial"] = 25

        # 4. Historical correlation footprint (max 15 pts)
        pop = context.get("affected_population", 0)
        if pop > 1000:
            signals["historical_similarity"] = 15
        elif pop > 0:
            signals["historical_similarity"] = 10

        # 5. LLM confidence component (max 10 pts)
        if llm_confidence is not None:
            signals["llm"] = int(min(max(llm_confidence, 0.0), 1.0) * 10)

        overall = sum(signals.values())
        overall = min(max(overall, 50), 100)

        return {"overall": overall, "signals": signals}
