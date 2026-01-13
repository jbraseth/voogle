# Copyright (c) 2025 Example Code
# Sample Python code for testing code content indexing

"""
Sample module demonstrating semantic search implementation.

This code is used as a test fixture for verifying that the indexing
pipeline correctly processes Python source code files.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchResult:
    """Represents a single search result with score and metadata."""

    text: str
    score: float
    source_id: str
    start_position: int
    end_position: int
    metadata: Optional[dict] = None

    def to_dict(self) -> dict:
        """Convert result to dictionary for JSON serialization."""
        return {
            "text": self.text,
            "score": self.score,
            "source_id": self.source_id,
            "start": self.start_position,
            "end": self.end_position,
            "metadata": self.metadata or {},
        }


class SemanticSearchEngine:
    """Simple semantic search engine implementation."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the search engine with an embedding model.

        Args:
            model_name: Name of the sentence transformer model to use.
        """
        self.model_name = model_name
        self._index: list[tuple[str, list[float]]] = []

    def add_document(self, doc_id: str, text: str) -> None:
        """Add a document to the search index.

        Args:
            doc_id: Unique identifier for the document.
            text: Text content to index.
        """
        # In real implementation, this would compute embeddings
        embedding = self._compute_embedding(text)
        self._index.append((doc_id, embedding))

    def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        """Search for documents similar to the query.

        Args:
            query: Search query text.
            top_k: Number of results to return.

        Returns:
            List of search results sorted by relevance.
        """
        query_embedding = self._compute_embedding(query)
        results = []

        for doc_id, doc_embedding in self._index:
            score = self._cosine_similarity(query_embedding, doc_embedding)
            results.append(
                SearchResult(
                    text=doc_id,  # Simplified for testing
                    score=score,
                    source_id=doc_id,
                    start_position=0,
                    end_position=100,
                )
            )

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def _compute_embedding(self, text: str) -> list[float]:
        """Compute embedding vector for text (stub for testing)."""
        # Return deterministic fake embedding based on text hash
        import hashlib

        h = hashlib.md5(text.encode()).hexdigest()
        return [int(c, 16) / 15.0 for c in h]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)


def main() -> None:
    """Example usage of the semantic search engine."""
    engine = SemanticSearchEngine()

    # Add some documents
    engine.add_document("doc1", "Python is a programming language")
    engine.add_document("doc2", "Machine learning with neural networks")
    engine.add_document("doc3", "Vector databases for semantic search")

    # Search
    results = engine.search("AI and deep learning", top_k=3)
    for result in results:
        print(f"{result.source_id}: {result.score:.4f}")


if __name__ == "__main__":
    main()
