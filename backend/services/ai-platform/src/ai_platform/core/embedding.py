import json
import os
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class EmbeddingResponse:
    vectors: list[list[float]]
    usage: dict[str, int]


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed_documents(self, texts: list[str]) -> EmbeddingResponse:
        """Generate vector embeddings for a list of document strings."""
        pass

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """Generate a single vector embedding for a query string."""
        pass


class GeminiEmbeddingAdapter(EmbeddingProvider):
    """
    Adapter for Gemini Text Embedding API using urllib REST calls.
    Target Model: models/text-embedding-004
    """

    def __init__(
        self, model_name: str = "text-embedding-004", api_key: str | None = None
    ) -> None:
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")

    async def embed_documents(self, texts: list[str]) -> EmbeddingResponse:
        if not self.api_key:
            # Return deterministic mock vectors when API key is missing
            mock_vectors = [self._mock_embed(text) for text in texts]
            return EmbeddingResponse(
                vectors=mock_vectors, usage={"prompt_tokens": 0, "total_tokens": 0}
            )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:batchEmbedContents?key={self.api_key}"

        requests_payload = []
        for text in texts:
            requests_payload.append(
                {
                    "model": f"models/{self.model_name}",
                    "content": {"parts": [{"text": text}]},
                }
            )

        payload = {"requests": requests_payload}
        headers = {"Content-Type": "application/json"}

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                resp_data = json.loads(response.read().decode("utf-8"))

            embeddings = resp_data.get("embeddings", [])
            vectors = [emb.get("values", []) for emb in embeddings]

            return EmbeddingResponse(
                vectors=vectors,
                usage={
                    "prompt_tokens": len(texts) * 10,
                    "total_tokens": len(texts) * 10,
                },
            )

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise RuntimeError(
                f"Gemini Embedding API failed with code {e.code}. Details: {error_body}"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch embeddings from Gemini API: {e}"
            ) from e

    async def embed_query(self, text: str) -> list[float]:
        resp = await self.embed_documents([text])
        if not resp.vectors:
            raise ValueError("Empty embedding vector returned.")
        return resp.vectors[0]

    def _mock_embed(self, text: str) -> list[float]:
        # Generate a deterministic mock vector of length 768
        vector = []
        # basic hash sum to seed
        seed = sum(ord(char) for char in text) % 1000
        for i in range(768):
            val = ((seed + i) * 31) % 1000
            vector.append(float(val) / 1000.0 - 0.5)
        return vector


class MockEmbeddingProvider(EmbeddingProvider):
    """
    Simulated embedding generator that provides deterministic mock vectors
    without network operations. Useful for local testing and CI loops.
    """

    def __init__(self, vector_size: int = 768) -> None:
        self.vector_size = vector_size
        self.call_count = 0

    async def embed_documents(self, texts: list[str]) -> EmbeddingResponse:
        self.call_count += 1
        vectors = []
        for text in texts:
            # Deterministic generation based on character code values
            seed = sum(ord(c) for c in text) % 200
            vec = [float((seed + j) % 13) / 13.0 for j in range(self.vector_size)]
            vectors.append(vec)
        return EmbeddingResponse(
            vectors=vectors, usage={"total_tokens": sum(len(t) for t in texts) // 4}
        )

    async def embed_query(self, text: str) -> list[float]:
        resp = await self.embed_documents([text])
        return resp.vectors[0]
