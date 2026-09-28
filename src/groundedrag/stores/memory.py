"""In-memory VectorStore — exact cosine similarity, no external dependency.

Reference implementation for tests and for trying groundedrag without a real
vector database. Pure Python, no numpy: this store is meant to be small
and always installable, not fast at scale.
"""

from __future__ import annotations

import math

from groundedrag.schemas import Chunk


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class InMemoryStore:
    """Keeps every chunk and vector in a plain dict — fine up to a few
    thousand chunks, which covers tests and small examples."""

    def __init__(self) -> None:
        self._chunks: dict[str, Chunk] = {}
        self._vectors: dict[str, list[float]] = {}

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must have the same length")
        for chunk, vector in zip(chunks, vectors, strict=True):
            self._chunks[chunk.id] = chunk
            self._vectors[chunk.id] = vector

    def query(
        self,
        vector: list[float],
        *,
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[Chunk]:
        allowed = set(document_ids) if document_ids is not None else None
        scored = [
            (chunk_id, _cosine_similarity(vector, chunk_vector))
            for chunk_id, chunk_vector in self._vectors.items()
            if allowed is None or self._chunks[chunk_id].document_id in allowed
        ]
        scored.sort(key=lambda item: item[1], reverse=True)
        return [self._chunks[chunk_id] for chunk_id, _ in scored[:top_k]]
