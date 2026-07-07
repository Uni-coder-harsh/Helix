from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class AgentResult(BaseModel):
    """Standardized result returned by every execution node in the AI decision pipeline."""

    agent_name: str = Field(description="Name of the agent executor")
    status: str = Field(default="SUCCESS", description="SUCCESS or FAILURE")
    confidence: float = Field(
        default=1.0, description="Confidence rating between 0.0 and 1.0"
    )
    execution_time_ms: float = Field(
        default=0.0, description="Execution latency in milliseconds"
    )
    inputs: dict[str, Any] = Field(
        default_factory=dict, description="Input parameters passed"
    )
    outputs: dict[str, Any] = Field(
        default_factory=dict, description="Output payload generated"
    )
    evidence: list[str] = Field(
        default_factory=list, description="Evidence facts collected"
    )
    warnings: list[str] = Field(default_factory=list, description="Warnings triggered")
    errors: list[str] = Field(default_factory=list, description="Errors encountered")
    next_agent: str | None = Field(
        default=None, description="Next suggested agent in pipeline"
    )


class BaseAgent(ABC):
    """Abstract base class establishing the contract for all AI Pipeline agents."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns unique identifier name for the agent."""
        pass

    @abstractmethod
    async def run(self, context: dict[str, Any]) -> AgentResult:
        """Executes the agent business logic over the provided context payload."""
        pass
