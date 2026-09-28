"""ChromaStore is tested against a real, ephemeral (in-process) Chroma
collection — no server, no persistence to disk, so it's safe to run in CI."""

from groundedrag.schemas import Chunk
from groundedrag.stores.chroma import ChromaStore


def test_add_and_query_roundtrip():
    store = ChromaStore(collection_name="test-collection")
    store.add(
        [
            Chunk(id="c1", document_id="doc-1", text="Reset the pump."),
            Chunk(id="c2", document_id="doc-2", text="Unrelated content."),
        ],
        [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
    )

    results = store.query([0.9, 0.1, 0.0], top_k=1)

    assert len(results) == 1
    assert results[0].id == "c1"
    assert results[0].document_id == "doc-1"
    assert results[0].text == "Reset the pump."


def test_query_filters_by_document_ids():
    store = ChromaStore(collection_name="test-collection-filtered")
    store.add(
        [
            Chunk(id="c1", document_id="doc-1", text="A"),
            Chunk(id="c2", document_id="doc-2", text="B"),
        ],
        [[1.0, 0.0], [1.0, 0.0]],
    )

    results = store.query([1.0, 0.0], top_k=5, document_ids=["doc-2"])

    assert [c.id for c in results] == ["c2"]


def test_add_with_no_chunks_is_a_no_op():
    store = ChromaStore(collection_name="test-collection-empty")
    store.add([], [])
    assert store.query([1.0, 0.0]) == []
