"""Tests for the dependency-free demo embedder."""

import math

from groundedrag.embeddings.hashing import HashingEmbedder


def test_same_text_yields_same_vector():
    embedder = HashingEmbedder()
    a, b = embedder.embed(["reset the pump", "reset the pump"])
    assert a == b


def test_different_text_yields_different_vectors():
    embedder = HashingEmbedder()
    a, b = embedder.embed(["reset the pump", "approve the invoice"])
    assert a != b


def test_vectors_are_unit_normalized():
    embedder = HashingEmbedder()
    [vector] = embedder.embed(["reset the pump before reassembly"])
    norm = math.sqrt(sum(v * v for v in vector))
    assert math.isclose(norm, 1.0, rel_tol=1e-9)


def test_empty_text_yields_zero_vector():
    embedder = HashingEmbedder(dimensions=16)
    [vector] = embedder.embed([""])
    assert vector == [0.0] * 16


def test_similar_texts_are_closer_than_unrelated_ones():
    embedder = HashingEmbedder()
    base, similar, unrelated = embedder.embed(
        [
            "reset the pump before reassembly",
            "reset the pump before you reassemble it",
            "approve the vendor invoice today",
        ]
    )

    def dot(a, b):
        return sum(x * y for x, y in zip(a, b, strict=True))

    assert dot(base, similar) > dot(base, unrelated)
