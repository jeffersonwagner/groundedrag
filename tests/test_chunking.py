"""Tests for the pure-Python text chunker shared by every loader."""

import pytest

from groundedrag.chunking import chunk_text


def test_short_text_is_a_single_chunk():
    assert chunk_text("hello world") == ["hello world"]


def test_empty_text_yields_no_chunks():
    assert chunk_text("   ") == []


def test_splits_long_text_on_whitespace():
    text = "word " * 300  # well over the default chunk_size
    chunks = chunk_text(text, chunk_size=50, overlap=10)

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 50
        # no chunk should start or end mid-word (a hyphenated split)
        assert not chunk.startswith(" ")


def test_consecutive_chunks_overlap():
    text = "word " * 300
    chunks = chunk_text(text, chunk_size=50, overlap=20)

    # the tail of one chunk should reappear at the head of the next
    assert chunks[0][-10:] in chunks[1]


def test_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=10, overlap=10)


def test_rejects_non_positive_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=0)
