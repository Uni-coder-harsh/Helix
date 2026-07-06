class ConfidenceScorer:
    """
    Computes a multi-dimensional confidence score (0.0 to 1.0)
    for generated recommendations, incorporating evidence, grounding,
    hallucination, and safety vectors.
    """

    def calculate_score(
        self,
        evidence_score: float,
        grounding_score: float,
        hallucination_detected: bool,
        safety_passed: bool,
    ) -> float:
        # If safety checks fail, confidence is absolute 0.0 (unsafe output)
        if not safety_passed:
            return 0.0

        # Base weight distribution
        # Grounding is 50% of the score (factual accuracy)
        # Evidence completeness is 50% of the score (input quality)
        base_score = (grounding_score * 0.5) + (evidence_score * 0.5)

        # Apply strict penalties
        if hallucination_detected:
            # Deduct 0.4 from final score for potential hallucinations
            base_score -= 0.4

        # Ensure score boundaries remain in [0.0, 1.0]
        return min(max(base_score, 0.0), 1.0)
