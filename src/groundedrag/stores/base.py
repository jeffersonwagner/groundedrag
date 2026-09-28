"""The VectorStore interface every retrieval backend implements.

See docs/adr/0001-domain-agnostic-core.md — groundedrag's core depends only
on this Protocol, never on a specific vector database's client. A
VectorStore deals in already-computed vectors, not raw text: embedding is
the caller's (or the retriever's) job via an Embedder, which keeps the
store swappable independently of the embedding backend.
"""

from __future__ import annotations

from typing import Protocol

from groundedrag.schemas import Chunk


class VectorStore(Protocol):
    """Minimal surface groundedrag needs from any vector backend."""

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Index ``chunks`` with their corresponding pre-computed ``vectors``."""
        ...

    def query(
        self,
        vector: list[float],
        *,
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[Chunk]:
        """Return the ``top_k`` chunks whose vectors are closest to ``vector``.

        When ``document_ids`` is given, results are restricted to chunks
        belonging to one of those documents — this is how the gate's
        coverage map narrows retrieval to only the documents cleared for
        the question's topic.
        """
        ...
