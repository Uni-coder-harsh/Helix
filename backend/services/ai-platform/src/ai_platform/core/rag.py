import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    doc_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGContext:
    retrieved_chunks: list[tuple[Document, float]]

    def format_as_text(self) -> str:
        """Formulate the context chunks into a clean, formatted text block for prompt consumption."""
        formatted = []
        for idx, (doc, score) in enumerate(self.retrieved_chunks):
            title = doc.metadata.get("title", f"Document-{doc.doc_id}")
            formatted.append(
                f"[{idx + 1}] Source: {title} (Relevance Score: {score:.4f})\n"
                f"Content: {doc.content}\n"
            )
        return "\n---\n".join(formatted)


class VectorStore(ABC):
    @abstractmethod
    async def add_documents(
        self, documents: list[Document], embeddings: list[list[float]]
    ) -> None:
        """Add documents and corresponding vector representations to the store."""
        pass

    @abstractmethod
    async def search(
        self, query_vector: list[float], top_k: int = 5
    ) -> list[tuple[Document, float]]:
        """Search the store for documents matching the query vector."""
        pass


class InMemoryVectorStore(VectorStore):
    """
    Pure Python implementation of a VectorStore using cosine similarity.
    Provides complete local functionality with zero external database dependencies.
    """

    def __init__(self) -> None:
        self.documents: list[Document] = []
        self.embeddings: list[list[float]] = []

    async def add_documents(
        self, documents: list[Document], embeddings: list[list[float]]
    ) -> None:
        if len(documents) != len(embeddings):
            raise ValueError(
                "Size mismatch: 'documents' and 'embeddings' must be of equal length."
            )
        self.documents.extend(documents)
        self.embeddings.extend(embeddings)

    async def search(
        self, query_vector: list[float], top_k: int = 5
    ) -> list[tuple[Document, float]]:
        if not self.documents:
            return []

        scored_results: list[tuple[Document, float]] = []
        for doc, emb in zip(self.documents, self.embeddings, strict=False):
            score = self._cosine_similarity(query_vector, emb)
            scored_results.append((doc, score))

        # Sort descending by similarity score
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:top_k]

    def _cosine_similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        if len(vec_a) != len(vec_b):
            # If dimensions mismatch, similarity is 0
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b, strict=False))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return dot_product / (norm_a * norm_b)


class RAGPipeline:
    """
    Orchestration class that maps inputs to embeddings, queries the vector store,
    compiles the retrieved context, and coordinates response generation.
    """

    def __init__(
        self, vector_store: VectorStore, embedding_provider: Any, llm_provider: Any
    ) -> None:
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self.llm_provider = llm_provider

    async def retrieve(self, query: str, top_k: int = 5) -> RAGContext:
        """Fetch matching documents based on query semantic embedding."""
        query_vector = await self.embedding_provider.embed_query(query)
        results = await self.vector_store.search(query_vector, top_k=top_k)
        return RAGContext(retrieved_chunks=results)

    async def generate_response(
        self, query: str, context: RAGContext, prompt_template: Any
    ) -> str:
        """Render context into a prompt template and execute LLM query."""
        formatted_context = context.format_as_text()
        rendered_prompt = prompt_template.render(
            issue_content=query,
            policies=formatted_context,
            evidence_summary="Refer to the attached source documents as ground truth.",
        )

        from ai_platform.core.llm import LLMMessage

        messages = [
            LLMMessage(
                role="system",
                content="You are a precise public governance reasoning assistant. Strictly ground your claims in the provided source policies.",
            ),
            LLMMessage(role="user", content=rendered_prompt),
        ]

        response = await self.llm_provider.generate(messages)
        return response.content
