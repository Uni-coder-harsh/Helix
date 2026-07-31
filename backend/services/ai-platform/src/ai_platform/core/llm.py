import json
import os
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


class ConfigurationError(ValueError):
    """Exception raised when there is a configuration error with LLM providers."""

    pass


@dataclass
class LLMMessage:
    role: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    content: str
    raw_response: dict[str, Any]
    usage: dict[str, int]
    model_name: str


class LLMProvider(ABC):
    @abstractmethod
    async def generate(
        self, messages: list[LLMMessage], config: dict[str, Any] | None = None
    ) -> LLMResponse:
        """Generate a response for the given list of messages."""
        pass

    @staticmethod
    def get_provider() -> "LLMProvider":
        provider_type = os.environ.get("LLM_PROVIDER", "").lower()
        if provider_type in ["openrouter", "open-router", "openrouter-gemma"]:
            return OpenRouterGemmaAdapter()
        if provider_type in ["gemini"]:
            return GeminiAdapter()
        if provider_type in [
            "gemma",
            "gemma-2",
            "gemma2",
            "gemma-2-9b-it",
            "gemma-2-27b-it",
        ]:
            if os.environ.get("OPENROUTER_API_KEY"):
                return OpenRouterGemmaAdapter()
            return GemmaAdapter()
        if provider_type == "mock":
            return MockProvider()
        # Default to OpenRouterGemmaAdapter if OPENROUTER_API_KEY is present
        if os.environ.get("OPENROUTER_API_KEY"):
            return OpenRouterGemmaAdapter()
        # Default to GemmaAdapter if GEMMA_API_KEY is present or LLM_PROVIDER is unset/empty
        if (
            os.environ.get("GEMMA_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
            or not provider_type
        ):
            return GemmaAdapter()
        raise ConfigurationError(
            f"Unsupported or missing LLM_PROVIDER: '{provider_type}'. Must be 'openrouter', 'gemma', 'gemini', or 'mock'."
        )


class GemmaAdapter(LLMProvider):
    """
    Concrete adapter for Google Gemma API models (e.g. Gemma 2 9B/27B/2B).
    Supports API requests via:
    1. Google AI Studio (generativelanguage.googleapis.com)
    2. Custom Gemma API URL / OpenRouter / HuggingFace endpoint (GEMMA_API_URL)

    Uses standard library urllib.request for lightweight, dependency-free execution.
    """

    def __init__(
        self, model_name: str | None = None, api_key: str | None = None
    ) -> None:
        self.model_name = model_name or os.environ.get("LLM_MODEL", "gemma-2-9b-it")
        self.api_key = (
            api_key
            or os.environ.get("GEMMA_API_KEY", "")
            or os.environ.get("GEMINI_API_KEY", "")
            or os.environ.get("HUGGINGFACE_API_KEY", "")
            or os.environ.get("HF_TOKEN", "")
        )
        self.api_url = os.environ.get("GEMMA_API_URL", "")

    async def generate(
        self, messages: list[LLMMessage], config: dict[str, Any] | None = None
    ) -> LLMResponse:
        if not self.api_key and not self.api_url:
            # Fallback for unauthenticated/test environments
            last_msg = messages[-1].content if messages else ""
            return LLMResponse(
                content=f"[GemmaAdapter Simulation - GEMMA_API_KEY / GEMINI_API_KEY not set] Analysis for prompt: {last_msg[:120]}...",
                raw_response={"status": "mocked", "reason": "no_api_key"},
                usage={
                    "prompt_tokens": 12,
                    "completion_tokens": 16,
                    "total_tokens": 28,
                },
                model_name=self.model_name,
            )

        generation_config = config or {}
        temp = generation_config.get(
            "temperature", float(os.environ.get("LLM_TEMPERATURE", "0.2"))
        )
        max_t = generation_config.get(
            "max_tokens", int(os.environ.get("LLM_MAX_TOKENS", "1024"))
        )
        timeout = float(os.environ.get("LLM_TIMEOUT", "30"))

        # Case A: Custom GEMMA_API_URL (OpenAI-compatible / HuggingFace Inference API)
        if self.api_url:
            payload = {
                "model": self.model_name,
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                "temperature": temp,
                "max_tokens": max_t,
            }
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.api_url, data=data, headers=headers, method="POST"
            )

            try:
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    resp_data = json.loads(response.read().decode("utf-8"))

                choices = resp_data.get("choices", [])
                if choices:
                    content_text = choices[0].get("message", {}).get("content", "")
                else:
                    content_text = str(resp_data)

                usage_meta = resp_data.get("usage", {})
                usage = {
                    "prompt_tokens": usage_meta.get("prompt_tokens", 0),
                    "completion_tokens": usage_meta.get("completion_tokens", 0),
                    "total_tokens": usage_meta.get("total_tokens", 0),
                }

                return LLMResponse(
                    content=content_text,
                    raw_response=resp_data,
                    usage=usage,
                    model_name=self.model_name,
                )
            except Exception as e:
                raise RuntimeError(
                    f"Gemma API request to {self.api_url} failed: {e}"
                ) from e

        # Case B: Google AI Studio Gemma API endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        contents_payload = []
        for msg in messages:
            role = "user" if msg.role in ["user", "system"] else "model"
            contents_payload.append({"role": role, "parts": [{"text": msg.content}]})

        payload = {
            "contents": contents_payload,
            "generationConfig": {
                "temperature": temp,
                "maxOutputTokens": max_t,
                "topP": generation_config.get("top_p", 0.95),
            },
        }

        system_msgs = [m for m in messages if m.role == "system"]
        if system_msgs:
            payload["systemInstruction"] = {
                "parts": [{"text": system_msgs[-1].content}]
            }

        headers = {"Content-Type": "application/json"}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                resp_data = json.loads(response.read().decode("utf-8"))

            candidates = resp_data.get("candidates", [])
            if not candidates:
                raise ValueError("Gemma API returned empty candidates response.")

            content_text = (
                candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            )

            usage_meta = resp_data.get("usageMetadata", {})
            usage = {
                "prompt_tokens": usage_meta.get("promptTokenCount", 0),
                "completion_tokens": usage_meta.get("candidatesTokenCount", 0),
                "total_tokens": usage_meta.get("totalTokenCount", 0),
            }

            return LLMResponse(
                content=content_text,
                raw_response=resp_data,
                usage=usage,
                model_name=self.model_name,
            )
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise RuntimeError(
                f"Gemma API request failed with status {e.code}. Details: {error_body}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Failed to communicate with Gemma API: {e}") from e


class OpenRouterGemmaAdapter(LLMProvider):
    """
    Concrete adapter for Google Gemma models hosted on OpenRouter API (openrouter.ai).
    Supports models like google/gemma-2-27b-it, google/gemma-2-9b-it.
    Uses standard library urllib.request for lightweight execution.
    """

    def __init__(
        self, model_name: str | None = None, api_key: str | None = None
    ) -> None:
        raw_model = model_name or os.environ.get("LLM_MODEL", "google/gemma-2-27b-it")
        if not raw_model.startswith("google/") and "/" not in raw_model:
            self.model_name = f"google/{raw_model}"
        else:
            self.model_name = raw_model

        self.api_key = (
            api_key
            or os.environ.get("OPENROUTER_API_KEY", "")
            or os.environ.get("GEMMA_API_KEY", "")
        )
        self.api_url = os.environ.get(
            "OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions"
        )

    async def generate(
        self, messages: list[LLMMessage], config: dict[str, Any] | None = None
    ) -> LLMResponse:
        if not self.api_key:
            last_msg = messages[-1].content if messages else ""
            return LLMResponse(
                content=f"[OpenRouter Gemma Simulation - OPENROUTER_API_KEY / GEMMA_API_KEY not set] Analysis for prompt: {last_msg[:120]}...",
                raw_response={"status": "mocked", "reason": "no_api_key"},
                usage={
                    "prompt_tokens": 12,
                    "completion_tokens": 16,
                    "total_tokens": 28,
                },
                model_name=self.model_name,
            )

        generation_config = config or {}
        temp = generation_config.get(
            "temperature", float(os.environ.get("LLM_TEMPERATURE", "0.2"))
        )
        max_t = generation_config.get(
            "max_tokens", int(os.environ.get("LLM_MAX_TOKENS", "1024"))
        )
        timeout = float(os.environ.get("LLM_TIMEOUT", "30"))

        payload = {
            "model": self.model_name,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temp,
            "max_tokens": max_t,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": os.environ.get("OPENROUTER_SITE_URL", "https://helix.dev"),
            "X-Title": os.environ.get(
                "OPENROUTER_SITE_NAME", "Project Helix Governance OS"
            ),
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.api_url, data=data, headers=headers, method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                resp_data = json.loads(response.read().decode("utf-8"))

            choices = resp_data.get("choices", [])
            if choices:
                content_text = choices[0].get("message", {}).get("content", "")
            else:
                content_text = str(resp_data)

            usage_meta = resp_data.get("usage", {})
            usage = {
                "prompt_tokens": usage_meta.get("prompt_tokens", 0),
                "completion_tokens": usage_meta.get("completion_tokens", 0),
                "total_tokens": usage_meta.get("total_tokens", 0),
            }

            return LLMResponse(
                content=content_text,
                raw_response=resp_data,
                usage=usage,
                model_name=self.model_name,
            )
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise RuntimeError(
                f"OpenRouter Gemma API failed ({e.code}): {error_body}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"OpenRouter Gemma API communication error: {e}") from e


class GeminiAdapter(LLMProvider):
    """
    Concrete adapter for Google Gemini API.
    Uses standard library urllib.request to avoid external SDK dependencies,
    ensuring lightweight build and robust runtime execution.
    """

    def __init__(
        self, model_name: str | None = None, api_key: str | None = None
    ) -> None:
        self.model_name = model_name or os.environ.get("LLM_MODEL", "gemini-1.5-flash")
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")

    async def generate(
        self, messages: list[LLMMessage], config: dict[str, Any] | None = None
    ) -> LLMResponse:
        if not self.api_key:
            # Fallback for testing/unauthenticated environments
            return LLMResponse(
                content=f"[GeminiAdapter Mock Response - GEMINI_API_KEY not set] Simulated response for input: {messages[-1].content}",
                raw_response={"status": "mocked", "reason": "no_api_key"},
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                model_name=self.model_name,
            )

        # Prepare URL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        # Format payload
        contents_payload = []
        for msg in messages:
            role = "user" if msg.role in ["user", "system"] else "model"
            contents_payload.append({"role": role, "parts": [{"text": msg.content}]})

        generation_config = config or {}
        temp = generation_config.get(
            "temperature", float(os.environ.get("LLM_TEMPERATURE", "0.2"))
        )
        max_t = generation_config.get(
            "max_tokens", int(os.environ.get("LLM_MAX_TOKENS", "1024"))
        )
        timeout = float(os.environ.get("LLM_TIMEOUT", "30"))

        payload = {
            "contents": contents_payload,
            "generationConfig": {
                "temperature": temp,
                "maxOutputTokens": max_t,
                "topP": generation_config.get("top_p", 0.95),
            },
        }

        # If there is a system instruction, set it in payload
        system_msgs = [m for m in messages if m.role == "system"]
        if system_msgs:
            payload["systemInstruction"] = {
                "parts": [{"text": system_msgs[-1].content}]
            }

        headers = {"Content-Type": "application/json"}

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                resp_data = json.loads(response.read().decode("utf-8"))

            candidates = resp_data.get("candidates", [])
            if not candidates:
                raise ValueError("Gemini returned empty candidates response.")

            content_text = (
                candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            )

            usage_meta = resp_data.get("usageMetadata", {})
            usage = {
                "prompt_tokens": usage_meta.get("promptTokenCount", 0),
                "completion_tokens": usage_meta.get("candidatesTokenCount", 0),
                "total_tokens": usage_meta.get("totalTokenCount", 0),
            }

            return LLMResponse(
                content=content_text,
                raw_response=resp_data,
                usage=usage,
                model_name=self.model_name,
            )

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise RuntimeError(
                f"Gemini API request failed with status {e.code}. Details: {error_body}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Failed to communicate with Gemini API: {e}") from e


class MockProvider(LLMProvider):
    """
    Mock LLM provider designed for local tests, development, and unit evaluation.
    Matches queries by direct substring and returns pre-programmed responses.
    """

    def __init__(self, default_response: str = "Mock Default Response") -> None:
        self.default_response = default_response
        self.rules: list[dict[str, Any]] = []
        self.calls: list[list[LLMMessage]] = []

    def register_rule(self, trigger_substring: str, response: str) -> None:
        self.rules.append({"trigger": trigger_substring, "response": response})

    async def generate(
        self, messages: list[LLMMessage], config: dict[str, Any] | None = None
    ) -> LLMResponse:
        _ = config
        self.calls.append(messages)
        last_content = messages[-1].content if messages else ""

        matched_response = self.default_response
        for rule in self.rules:
            if rule["trigger"] in last_content:
                matched_response = rule["response"]
                break

        return LLMResponse(
            content=matched_response,
            raw_response={"status": "mocked", "rule_applied": True},
            usage={
                "prompt_tokens": 10,
                "completion_tokens": len(matched_response) // 4,
                "total_tokens": 10 + (len(matched_response) // 4),
            },
            model_name="mock-provider",
        )
