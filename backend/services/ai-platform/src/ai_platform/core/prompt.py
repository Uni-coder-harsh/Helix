from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class PromptTemplate:
    name: str
    template_str: str
    version: str
    input_variables: list[str]
    description: str = ""

    def render(self, **kwargs: Any) -> str:
        """Render the prompt template with provided keyword arguments."""
        missing = [var for var in self.input_variables if var not in kwargs]
        if missing:
            raise ValueError(
                f"Missing required input variables for prompt rendering: {missing}"
            )

        try:
            return self.template_str.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Failed rendering prompt template. KeyError: {e}") from e


class PromptVersionControl(ABC):
    @abstractmethod
    def get_prompt(self, name: str, version: str | None = None) -> PromptTemplate:
        """Retrieve a prompt template by name and optionally by specific version."""
        pass

    @abstractmethod
    def save_prompt(self, template: PromptTemplate) -> None:
        """Save a new prompt template version."""
        pass

    @abstractmethod
    def list_prompts(self) -> list[dict[str, Any]]:
        """List all registered prompt templates and their versions."""
        pass


class InMemoryPromptRegistry(PromptVersionControl):
    """
    In-memory implementation of the PromptVersionControl interface.
    Preloaded with core system prompt templates for governance reasoning, evidence validation,
    safety assessment, and hallucination checks.
    """

    def __init__(self) -> None:
        # Map: name -> list of PromptTemplate (sorted by version ascending or chronological)
        self._registry: dict[str, list[PromptTemplate]] = {}
        self._bootstrap_default_prompts()

    def get_prompt(self, name: str, version: str | None = None) -> PromptTemplate:
        if name not in self._registry or not self._registry[name]:
            raise KeyError(f"Prompt template '{name}' not found in registry.")

        templates = self._registry[name]
        if version is None:
            # Return latest version
            return templates[-1]

        for t in templates:
            if t.version == version:
                return t

        raise KeyError(f"Prompt template '{name}' with version '{version}' not found.")

    def save_prompt(self, template: PromptTemplate) -> None:
        if template.name not in self._registry:
            self._registry[template.name] = []

        # Check if version already exists
        existing = self._registry[template.name]
        for i, t in enumerate(existing):
            if t.version == template.version:
                # Overwrite
                existing[i] = template
                return

        existing.append(template)

    def list_prompts(self) -> list[dict[str, Any]]:
        results = []
        for name, templates in self._registry.items():
            results.append(
                {
                    "name": name,
                    "latest_version": templates[-1].version,
                    "available_versions": [t.version for t in templates],
                    "description": templates[-1].description,
                }
            )
        return results

    def _bootstrap_default_prompts(self) -> None:
        # Bootstrap default reasoning prompt
        reasoning_str = (
            "You are the Helix Reasoning Engine.\n"
            "Analyze the following citizen issue and identify relevant policies and guidelines.\n\n"
            "Citizen Issue:\n{issue_content}\n\n"
            "Retrieved Policies:\n{policies}\n\n"
            "Evidence Summary:\n{evidence_summary}\n\n"
            "Provide a step-by-step reasoning chain and recommend an action. Format output as JSON."
        )
        self.save_prompt(
            PromptTemplate(
                name="governance_reasoning",
                template_str=reasoning_str,
                version="1.0.0",
                input_variables=["issue_content", "policies", "evidence_summary"],
                description="Core prompt template for analyzing citizen complaints against active policy rules.",
            )
        )

        # Bootstrap evidence engine prompt
        evidence_str = (
            "You are the Helix Evidence Analyzer.\n"
            "Examine the following documents/metadata and extract facts.\n\n"
            "Required Evidence for Scheme/Action:\n{required_schema}\n\n"
            "Provided Evidentiary Materials:\n{provided_evidence}\n\n"
            "Extract: 1. Verified Facts, 2. Gaps, 3. Discrepancies. Format output as JSON."
        )
        self.save_prompt(
            PromptTemplate(
                name="evidence_validation",
                template_str=evidence_str,
                version="1.0.0",
                input_variables=["required_schema", "provided_evidence"],
                description="Extracts structured facts and verifies requirements from evidence files.",
            )
        )

        # Bootstrap safety audit prompt
        safety_str = (
            "You are the Helix Safety Audit Layer.\n"
            "Analyze the text below for sensitive PII leaks, toxic speech, or administrative bypass attempts.\n\n"
            "Content:\n{content}\n\n"
            "Respond with a JSON object containing 'is_safe' (boolean), 'flagged_categories' (list), and 'risk_rationale' (string)."
        )
        self.save_prompt(
            PromptTemplate(
                name="safety_compliance",
                template_str=safety_str,
                version="1.0.0",
                input_variables=["content"],
                description="Evaluates input/output content against platform guardrails.",
            )
        )

        # Bootstrap grounding prompt
        grounding_str = (
            "You are the Helix Grounding Layer.\n"
            "Compare the claims in the response against the official source text.\n\n"
            "Source Policy & Evidence:\n{sources}\n\n"
            "Response Claims:\n{claims}\n\n"
            "Verify if each claim is directly grounded in the sources. Identify any ungrounded assertions."
        )
        self.save_prompt(
            PromptTemplate(
                name="grounding_verification",
                template_str=grounding_str,
                version="1.0.0",
                input_variables=["sources", "claims"],
                description="Compares LLM response claims with source texts to confirm factual alignment.",
            )
        )
