"""pgvector implementation of VectorStore.

Requires a Postgres instance with the ``vector`` extension enabled and the
``pgvector`` extra installed. Not covered by this repository's default CI
(no live Postgres instance) — contributions with a docker-compose-based
integration test are welcome.
"""

from __future__ import annotations

from groundedrag.schemas import Chunk


class PgVectorStore:
    def __init__(self, dsn: str, table: str = "groundedrag_chunks") -> None:
        self.dsn = dsn
        self.table = table

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        raise NotImplementedError(
            "PgVectorStore is not implemented yet — contributions welcome. "
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
            "PgVectorStore is not implemented yet — contributions welcome. "
            "Use ChromaStore or InMemoryStore in the meantime."
        )
