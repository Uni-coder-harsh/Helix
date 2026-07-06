import re

from ai_platform.engines.policy import PolicyDocument
from ai_platform.engines.reasoning import ReasoningOutcome


class HallucinationGuard:
    """
    Scans generated reasoning outcomes to detect potential factual hallucinations,
    self-contradictions, or policy limit inflation.
    """

    async def detect_hallucinations(
        self, reasoning_outcome: ReasoningOutcome, policies: list[PolicyDocument]
    ) -> bool:
        rationale_lower = reasoning_outcome.rationale.lower()

        # 1. Contradiction Check: Check if conflicting decisions are mentioned
        if (
            ("approve" in rationale_lower)
            and ("reject" in rationale_lower)
            and self._has_unresolved_contradiction(rationale_lower)
        ):
            return True

        # 2. SLA Limit Hallucination Check
        # Match SLA limits in policy metadata and check if rationale
        # mentions a different number followed by "hours"
        for policy in policies:
            policy_sla = policy.metadata.get("sla_hours")
            if policy_sla is not None:
                # Find all patterns of "X hours" or "SLA of X" in the rationale
                hour_matches = re.findall(r"\b(\d+)\s*(?:hour|hr)", rationale_lower)
                for match in hour_matches:
                    val = int(match)
                    # Allow tolerance for standard math divisions (e.g., 24 vs 48)
                    # but flag wild differences
                    if (
                        val != policy_sla
                        and (val % 24 == 0)
                        and (val > policy_sla * 2 or val < policy_sla / 4)
                    ):
                        return True

        # 3. Empty Chain-of-Thought Validation
        # If the model gives a verdict but no actual reasoning steps,
        # flag as anomalous hallucination.
        return bool(
            not reasoning_outcome.chain_of_thought
            and reasoning_outcome.verdict != "REVIEW_REQUIRED"
        )

    def _has_unresolved_contradiction(self, text: str) -> bool:
        # Check if "approve" and "reject" (or similar antonyms) occur near each other,
        # indicating logical confusion.
        pattern = r"\b(approve|validated)\b.{1,100}\b(reject|deny|denied)\b"
        return bool(
            re.search(pattern, text)
            or re.search(
                r"\b(reject|deny|denied)\b.{1,100}\b(approve|validated)\b", text
            )
        )
