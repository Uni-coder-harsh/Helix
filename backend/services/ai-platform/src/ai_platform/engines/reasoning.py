import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from ai_platform.core.llm import LLMMessage, LLMProvider
from ai_platform.core.prompt import PromptVersionControl
from ai_platform.engines.evidence import EvidenceAssessment
from ai_platform.engines.policy import PolicyDocument


@dataclass
class ReasoningStep:
    step_number: int
    thought: str
    conclusion: str


@dataclass
class ReasoningOutcome:
    chain_of_thought: list[ReasoningStep]
    verdict: str
    rationale: str
    policies_applied: list[str]
    grounding_references: list[str]
    raw_response: str | None = None


class ReasoningEngine(ABC):
    @abstractmethod
    async def reason_about_issue(
        self,
        issue: dict[str, Any],
        policies: list[PolicyDocument],
        evidence: EvidenceAssessment,
    ) -> ReasoningOutcome:
        """Perform systematic policy reasoning over an issue, applying policies and evidence."""
        pass


class LLMReasoningEngine(ReasoningEngine):
    """
    LLM-powered policy reasoning agent.
    Utilizes chain-of-thought prompt templates to generate verifiable verdicts.
    """

    def __init__(
        self, llm_provider: LLMProvider, prompt_registry: PromptVersionControl
    ) -> None:
        self.llm_provider = llm_provider
        self.prompt_registry = prompt_registry

    async def reason_about_issue(
        self,
        issue: dict[str, Any],
        policies: list[PolicyDocument],
        evidence: EvidenceAssessment,
    ) -> ReasoningOutcome:
        # Build policy reference block
        policies_str = (
            "\n\n".join(
                f"Policy ID: {p.policy_id}\nTitle: {p.title}\nContent: {p.content}"
                for p in policies
            )
            if policies
            else "No policies retrieved for this category."
        )

        # Format evidence assessment summary
        evidence_summary = (
            f"Evidence Sufficiency: {evidence.is_sufficient}\n"
            f"Extracted Facts: {json.dumps(evidence.extracted_facts)}\n"
            f"Missing Fields: {evidence.missing_fields}\n"
            f"Discrepancies: {evidence.discrepancies}"
        )

        # Load prompt template
        template = self.prompt_registry.get_prompt("governance_reasoning")
        rendered = template.render(
            issue_content=issue.get("content", ""),
            policies=policies_str,
            evidence_summary=evidence_summary,
        )

        messages = [
            LLMMessage(
                role="system",
                content="You are the reasoning engine of a public governance system. Output raw JSON ONLY. Do not include markdown code block wrapping.",
            ),
            LLMMessage(role="user", content=rendered),
        ]

        response = await self.llm_provider.generate(messages)

        return self._parse_llm_response(response.content, policies)

    def _parse_llm_response(
        self, text: str, policies: list[PolicyDocument]
    ) -> ReasoningOutcome:
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)

            steps = []
            for item in data.get("chain_of_thought", []):
                steps.append(
                    ReasoningStep(
                        step_number=int(item.get("step_number", 1)),
                        thought=item.get("thought", ""),
                        conclusion=item.get("conclusion", ""),
                    )
                )

            return ReasoningOutcome(
                chain_of_thought=steps,
                verdict=data.get("verdict", "REJECTED"),
                rationale=data.get("rationale", "No rationale returned."),
                policies_applied=data.get(
                    "policies_applied", [p.policy_id for p in policies]
                ),
                grounding_references=data.get("grounding_references", []),
                raw_response=cleaned,
            )

        except (json.JSONDecodeError, ValueError, TypeError):
            # Fallback when JSON parser fails
            return ReasoningOutcome(
                chain_of_thought=[
                    ReasoningStep(
                        step_number=1,
                        thought="Manual recovery due to parsing failure.",
                        conclusion="Unable to parse LLM structured reasoning steps.",
                    )
                ],
                verdict="REVIEW_REQUIRED",
                rationale=f"Failed parsing reasoning JSON output. Raw: {cleaned}",
                policies_applied=[p.policy_id for p in policies],
                grounding_references=[],
                raw_response=cleaned,
            )
