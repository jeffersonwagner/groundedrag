"""Tests for the plain-text/Markdown loader."""

from groundedrag.loaders.text import load_text


def test_load_text_produces_document_and_chunks(tmp_path):
    path = tmp_path / "policy.md"
    path.write_text("Employees may work remotely up to three days a week.")

    document, chunks = load_text(path)

    assert document.id == "policy"
    assert document.source == str(path)
    assert len(chunks) == 1
    assert chunks[0].document_id == "policy"
    assert "remotely" in chunks[0].text


def test_load_text_chunks_long_content(tmp_path):
    path = tmp_path / "manual.txt"
    path.write_text("word " * 300)

    _, chunks = load_text(path, chunk_size=50, overlap=10)

    assert len(chunks) > 1
    assert all(chunk.document_id == "manual" for chunk in chunks)
    # ids are unique and ordered
    assert [c.id for c in chunks] == [f"manual::{i}" for i in range(len(chunks))]
