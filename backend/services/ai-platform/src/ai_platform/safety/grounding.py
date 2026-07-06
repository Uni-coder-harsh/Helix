import re
from dataclasses import dataclass, field

from ai_platform.engines.evidence import EvidenceAssessment
from ai_platform.engines.policy import PolicyDocument
from ai_platform.engines.reasoning import ReasoningOutcome


@dataclass
class GroundingResult:
    grounding_score: float
    warnings: list[str] = field(default_factory=list)


class GroundingLayer:
    """
    Verifies that ReasoningEngine outputs are factually grounded in the source
    policies and evidence assessment facts. Detects out-of-context claims.
    """

    async def verify_grounding(
        self,
        reasoning_outcome: ReasoningOutcome,
        policies: list[PolicyDocument],
        evidence: EvidenceAssessment,
    ) -> GroundingResult:
        warnings = []

        # Collect source text corpora
        source_texts = []
        for policy in policies:
            source_texts.append(policy.content.lower())
            source_texts.append(policy.title.lower())

        # Add evidence facts
        for key, val in evidence.extracted_facts.items():
            source_texts.append(f"{key}: {val}".lower())

        combined_sources = " ".join(source_texts)

        # 1. Check if policies mentioned in reasoning outcome were actually retrieved
        retrieved_ids = {p.policy_id for p in policies}
        for applied_id in reasoning_outcome.policies_applied:
            if applied_id not in retrieved_ids:
                warnings.append(
                    f"Reasoning referenced policy '{applied_id}' which was not in retrieved context."
                )

        # 2. Compute token/number overlap matching
        # Extract all numbers from the rationale
        rationale_numbers = set(re.findall(r"\b\d+\b", reasoning_outcome.rationale))
        source_numbers = set(re.findall(r"\b\d+\b", combined_sources))

        unsupported_numbers = rationale_numbers - source_numbers
        # Filter out standard low numbers or index counters (0, 1, 2, 5) to avoid false flags
        unsupported_numbers = {num for num in unsupported_numbers if int(num) > 5}

        if unsupported_numbers:
            warnings.append(
                f"Rationale contains numerical facts/limits not found in sources: {list(unsupported_numbers)}"
            )

        # 3. Term overlap ratio
        rationale_words = self._tokenize(reasoning_outcome.rationale)
        source_words = self._tokenize(combined_sources)

        # We look for key terms (length > 5) in rationale that are also present in sources
        key_rationale_words = {w for w in rationale_words if len(w) > 5}
        if not key_rationale_words:
            grounding_score = 1.0
        else:
            intersection = key_rationale_words.intersection(source_words)
            grounding_score = len(intersection) / len(key_rationale_words)

        # Adjust score downward for warnings
        for _ in warnings:
            grounding_score = max(grounding_score - 0.15, 0.0)

        return GroundingResult(
            grounding_score=round(grounding_score, 4), warnings=warnings
        )

    def _tokenize(self, text: str) -> set[str]:
        # Simple lowercase word tokens extractor
        words = re.findall(r"\b[a-z]{3,}\b", text.lower())
        return set(words)
