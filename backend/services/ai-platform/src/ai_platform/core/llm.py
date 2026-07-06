import json
import os
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


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


class GeminiAdapter(LLMProvider):
    """
    Concrete adapter for Google Gemini API.
    Uses standard library urllib.request to avoid external SDK dependencies,
    ensuring lightweight build and robust runtime execution.
    """

    def __init__(
        self, model_name: str = "gemini-1.5-flash", api_key: str | None = None
    ) -> None:
        self.model_name = model_name
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
            # Gemini roles: "user" or "model"
            role = "user" if msg.role in ["user", "system"] else "model"
            contents_payload.append({"role": role, "parts": [{"text": msg.content}]})

        generation_config = config or {}
        payload = {
            "contents": contents_payload,
            "generationConfig": {
                "temperature": generation_config.get("temperature", 0.2),
                "maxOutputTokens": generation_config.get("max_tokens", 1024),
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
            with urllib.request.urlopen(req, timeout=30) as response:
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
