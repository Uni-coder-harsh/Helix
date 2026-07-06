import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ai_platform.core.llm import LLMMessage, LLMProvider
from ai_platform.core.prompt import PromptVersionControl


@dataclass
class EvidenceFile:
    file_id: str
    file_name: str
    file_type: str
    extracted_text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceAssessment:
    is_sufficient: bool
    extracted_facts: dict[str, Any]
    missing_fields: list[str]
    discrepancies: list[str]
    confidence_score: float
    raw_analysis: str | None = None


class EvidenceEngine(ABC):
    @abstractmethod
    async def assess_evidence(
        self, files: list[EvidenceFile], requirements: dict[str, Any]
    ) -> EvidenceAssessment:
        """Analyze evidentiary files against structured schema requirements."""
        pass


class LLMEvidenceEngine(EvidenceEngine):
    """
    LLM-powered evidence analyzer.
    Leverages LLM Provider and prompt templates to audit files and verify compliance.
    """

    def __init__(
        self, llm_provider: LLMProvider, prompt_registry: PromptVersionControl
    ) -> None:
        self.llm_provider = llm_provider
        self.prompt_registry = prompt_registry

    async def assess_evidence(
        self, files: list[EvidenceFile], requirements: dict[str, Any]
    ) -> EvidenceAssessment:
        if not files:
            return EvidenceAssessment(
                is_sufficient=False,
                extracted_facts={},
                missing_fields=requirements.get("required_keys", []),
                discrepancies=["No evidence files uploaded."],
                confidence_score=0.0,
            )

        # Build context of provided evidence
        provided_evidence_list = []
        for file in files:
            provided_evidence_list.append(
                f"File: {file.file_name} (ID: {file.file_id}, Type: {file.file_type})\n"
                f"Content Text Extract:\n{file.extracted_text}\n"
                f"Metadata: {json.dumps(file.metadata)}"
            )
        provided_evidence_str = "\n\n".join(provided_evidence_list)

        # Load prompt template
        template = self.prompt_registry.get_prompt("evidence_validation")
        rendered = template.render(
            required_schema=json.dumps(requirements, indent=2),
            provided_evidence=provided_evidence_str,
        )

        messages = [
            LLMMessage(
                role="system",
                content="You are a strict legal and administrative compliance checker. Output raw JSON ONLY. Do not include markdown code block formatting like ```json ... ``` in your output.",
            ),
            LLMMessage(role="user", content=rendered),
        ]

        response = await self.llm_provider.generate(messages)

        return self._parse_llm_response(response.content)

    def _parse_llm_response(self, text: str) -> EvidenceAssessment:
        # Clean potential markdown output
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
            return EvidenceAssessment(
                is_sufficient=data.get("is_sufficient", False),
                extracted_facts=data.get("extracted_facts", {}),
                missing_fields=data.get("missing_fields", []),
                discrepancies=data.get("discrepancies", []),
                confidence_score=float(data.get("confidence_score", 0.5)),
                raw_analysis=cleaned,
            )
        except (json.JSONDecodeError, ValueError, TypeError):
            # Fallback parsing in case of non-conformant JSON output
            is_sufficient = (
                "sufficient" in cleaned.lower()
                and "insufficient" not in cleaned.lower()
            )
            return EvidenceAssessment(
                is_sufficient=is_sufficient,
                extracted_facts={"raw_unparsed_analysis": cleaned},
                missing_fields=[],
                discrepancies=[
                    "Failed to parse LLM analysis output as valid JSON. Raw output captured."
                ],
                confidence_score=0.3,
                raw_analysis=cleaned,
            )
