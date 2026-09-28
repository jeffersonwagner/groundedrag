"""Tests for the in-memory reference VectorStore."""

import pytest

from groundedrag.schemas import Chunk
from groundedrag.stores.memory import InMemoryStore


def _chunk(chunk_id: str, document_id: str, text: str = "") -> Chunk:
    return Chunk(id=chunk_id, document_id=document_id, text=text)


def test_query_returns_closest_vector_first():
    store = InMemoryStore()
    store.add(
        [_chunk("a", "doc-1"), _chunk("b", "doc-1"), _chunk("c", "doc-1")],
        [[1.0, 0.0], [0.0, 1.0], [0.9, 0.1]],
    )

    results = store.query([1.0, 0.0], top_k=2)

    assert [c.id for c in results] == ["a", "c"]


def test_query_filters_by_document_ids():
    store = InMemoryStore()
    store.add(
        [_chunk("a", "doc-1"), _chunk("b", "doc-2")],
        [[1.0, 0.0], [1.0, 0.0]],
    )

    results = store.query([1.0, 0.0], top_k=5, document_ids=["doc-2"])

    assert [c.id for c in results] == ["b"]


def test_query_with_empty_document_ids_returns_nothing():
    store = InMemoryStore()
    store.add([_chunk("a", "doc-1")], [[1.0, 0.0]])

    assert store.query([1.0, 0.0], document_ids=[]) == []


def test_add_rejects_mismatched_lengths():
    store = InMemoryStore()
    with pytest.raises(ValueError):
        store.add([_chunk("a", "doc-1")], [[1.0, 0.0], [0.0, 1.0]])


def test_query_on_empty_store_returns_nothing():
    store = InMemoryStore()
    assert store.query([1.0, 0.0]) == []
