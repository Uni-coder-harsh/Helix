import os

import pytest
from ai_platform.core.llm import (
    GemmaAdapter,
    LLMMessage,
    LLMProvider,
    OpenRouterGemmaAdapter,
)


def test_gemma_adapter_initialization() -> None:
    adapter = GemmaAdapter(model_name="gemma-2-9b-it")
    assert adapter.model_name == "gemma-2-9b-it"


def test_openrouter_gemma_adapter_initialization() -> None:
    adapter = OpenRouterGemmaAdapter(model_name="gemma-2-27b-it")
    assert adapter.model_name == "google/gemma-2-27b-it"


@pytest.mark.asyncio
async def test_openrouter_gemma_adapter_fallback() -> None:
    old_key = os.environ.pop("OPENROUTER_API_KEY", None)
    old_gemma_key = os.environ.pop("GEMMA_API_KEY", None)
    try:
        adapter = OpenRouterGemmaAdapter(model_name="google/gemma-2-27b-it")
        messages = [LLMMessage(role="user", content="Analyze Ward 12 issue")]
        response = await adapter.generate(messages)

        assert response.model_name == "google/gemma-2-27b-it"
        assert response.content is not None
        assert "OpenRouter Gemma Simulation" in response.content
    finally:
        if old_key:
            os.environ["OPENROUTER_API_KEY"] = old_key
        if old_gemma_key:
            os.environ["GEMMA_API_KEY"] = old_gemma_key


@pytest.mark.asyncio
async def test_gemma_adapter_fallback_generation() -> None:
    # Ensure no API keys in test environment for simulation fallback check
    old_key = os.environ.pop("GEMMA_API_KEY", None)
    old_gemini_key = os.environ.pop("GEMINI_API_KEY", None)
    try:
        adapter = GemmaAdapter(model_name="gemma-2-9b-it")
        messages = [LLMMessage(role="user", content="Analyze Ward 12 issue")]
        response = await adapter.generate(messages)

        assert response.model_name == "gemma-2-9b-it"
        assert response.content is not None
        assert (
            "GemmaAdapter" in response.content
            or "mocked" in response.raw_response.get("status", "")
        )
    finally:
        if old_key:
            os.environ["GEMMA_API_KEY"] = old_key
        if old_gemini_key:
            os.environ["GEMINI_API_KEY"] = old_gemini_key


def test_llm_provider_factory_defaults_to_gemma() -> None:
    provider = LLMProvider.get_provider()
    assert isinstance(provider, (GemmaAdapter, OpenRouterGemmaAdapter))
