"""Wires an Embedder and a VectorStore to the DocumentGate.

This is the one place in groundedrag's core that talks to both the gate and
the storage layer — everything upstream (callers) only sees `retrieve()`,
and everything downstream (providers, stores, embedders) only sees the
Protocol it implements.
"""

from __future__ import annotations

from groundedrag.embeddings.base import Embedder
from groundedrag.gate import DocumentGate
from groundedrag.schemas import Chunk, GateDecision
from groundedrag.stores.base import VectorStore


class GatedRetriever:
    """Retrieves chunks for a topic only if the gate allows it.

    Retrieval is scoped to the documents the coverage map maps to that
    topic (via ``document_ids``), not to the whole index — the same
    principle as the original coverage-map design: a document can cover
    several topics, and only the topics it actually covers narrow
    retrieval.
    """

    def __init__(self, gate: DocumentGate, store: VectorStore, embedder: Embedder) -> None:
        self._gate = gate
        self._store = store
        self._embedder = embedder

    def retrieve(
        self, topic: str, query: str, *, top_k: int = 5
    ) -> tuple[GateDecision, list[Chunk]]:
        """Return the gate's decision and, if allowed, the retrieved chunks.

        A refused decision always comes back with an empty chunk list —
        the store is never even queried, let alone an LLM called.
        """
        decision = self._gate.check(topic)
        if not decision.allowed:
            return decision, []

        document_ids = self._gate.coverage.documents_for(topic)
        [vector] = self._embedder.embed([query])
        chunks = self._store.query(vector, top_k=top_k, document_ids=document_ids)
        return decision, chunks
