# Helix AI Platform Service Monorepo Package Foundation
# Phase 1: Modular Monolith Framework

from ai_platform.core import (
    Document,
    EmbeddingProvider,
    EmbeddingResponse,
    GeminiAdapter,
    GeminiEmbeddingAdapter,
    InMemoryPromptRegistry,
    InMemoryVectorStore,
    LLMMessage,
    LLMProvider,
    LLMResponse,
    MockEmbeddingProvider,
    MockProvider,
    PromptTemplate,
    PromptVersionControl,
    RAGContext,
    RAGPipeline,
    VectorStore,
)
from ai_platform.engines import (
    EvidenceAssessment,
    EvidenceEngine,
    EvidenceFile,
    InMemoryPolicyRegistry,
    LLMEvidenceEngine,
    LLMReasoningEngine,
    OrchestratedRecommendationEngine,
    PolicyDocument,
    PolicyRetrievalInterface,
    ReasoningEngine,
    ReasoningOutcome,
    ReasoningStep,
    Recommendation,
    RecommendationEngine,
)
from ai_platform.evaluation import (
    EvalCase,
    EvalCaseResult,
    EvalMetricResult,
    EvalSuiteResult,
    EvaluationSuite,
    get_default_evaluation_dataset,
)
from ai_platform.safety import (
    ConfidenceScorer,
    GroundingLayer,
    GroundingResult,
    HallucinationGuard,
    SafetyGuard,
)

__version__ = "1.0.0"

__all__ = [
    # Core
    "LLMMessage",
    "LLMResponse",
    "LLMProvider",
    "GeminiAdapter",
    "MockProvider",
    "PromptTemplate",
    "PromptVersionControl",
    "InMemoryPromptRegistry",
    "EmbeddingResponse",
    "EmbeddingProvider",
    "GeminiEmbeddingAdapter",
    "MockEmbeddingProvider",
    "Document",
    "RAGContext",
    "VectorStore",
    "InMemoryVectorStore",
    "RAGPipeline",
    # Engines
    "PolicyDocument",
    "PolicyRetrievalInterface",
    "InMemoryPolicyRegistry",
    "EvidenceFile",
    "EvidenceAssessment",
    "EvidenceEngine",
    "LLMEvidenceEngine",
    "ReasoningStep",
    "ReasoningOutcome",
    "ReasoningEngine",
    "LLMReasoningEngine",
    "Recommendation",
    "RecommendationEngine",
    "OrchestratedRecommendationEngine",
    # Safety
    "SafetyGuard",
    "GroundingResult",
    "GroundingLayer",
    "HallucinationGuard",
    "ConfidenceScorer",
    # Evaluation
    "EvalCase",
    "get_default_evaluation_dataset",
    "EvalMetricResult",
    "EvalCaseResult",
    "EvalSuiteResult",
    "EvaluationSuite",
]
