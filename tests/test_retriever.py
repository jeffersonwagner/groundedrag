"""Tests for GatedRetriever — the core guarantee end to end: no coverage,
no query, no chunks, ever."""

from groundedrag.coverage import CoverageMap
from groundedrag.gate import DocumentGate
from groundedrag.retriever import GatedRetriever
from groundedrag.schemas import Chunk
from groundedrag.stores.memory import InMemoryStore


class FakeEmbedder:
    """Deterministic stand-in for a real embedding backend in tests."""

    def __init__(self, vectors_by_text: dict[str, list[float]]) -> None:
        self._vectors_by_text = vectors_by_text
        self.calls: list[list[str]] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)
        return [self._vectors_by_text[text] for text in texts]


def test_refused_topic_never_touches_the_store():
    gate = DocumentGate(CoverageMap({}))
    store = InMemoryStore()
    embedder = FakeEmbedder({})
    retriever = GatedRetriever(gate, store, embedder)

    decision, chunks = retriever.retrieve("payroll", "when do I get paid?")

    assert decision.allowed is False
    assert chunks == []
    assert embedder.calls == []  # the query was never even embedded


def test_allowed_topic_scopes_retrieval_to_its_documents():
    gate = DocumentGate(CoverageMap({"billing": ["doc-1"]}))
    store = InMemoryStore()
    store.add(
        [
            Chunk(id="c1", document_id="doc-1", text="billing chunk"),
            Chunk(id="c2", document_id="doc-2", text="unrelated chunk"),
        ],
        [[1.0, 0.0], [1.0, 0.0]],
    )
    embedder = FakeEmbedder({"how do refunds work?": [1.0, 0.0]})
    retriever = GatedRetriever(gate, store, embedder)

    decision, chunks = retriever.retrieve("billing", "how do refunds work?")

    assert decision.allowed is True
    assert [c.id for c in chunks] == ["c1"]  # doc-2 is not mapped to "billing"
