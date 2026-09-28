"""Qdrant implementation of VectorStore.

Requires a running Qdrant instance and the ``qdrant`` extra. Not covered by
this repository's default CI (no live Qdrant instance) — contributions
with a docker-compose-based integration test are welcome.
"""

from __future__ import annotations

from groundedrag.schemas import Chunk


class QdrantStore:
    def __init__(
        self,
        collection_name: str = "groundedrag",
        url: str = "http://localhost:6333",
    ) -> None:
        self.collection_name = collection_name
        self.url = url

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        raise NotImplementedError(
            "QdrantStore is not implemented yet — contributions welcome. "
            "Use ChromaStore or InMemoryStore in the meantime."
        )

    def query(
        self,
        vector: list[float],
        *,
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[Chunk]:
        raise NotImplementedError(
            "QdrantStore is not implemented yet — contributions welcome. "
            "Use ChromaStore or InMemoryStore in the meantime."
        )
