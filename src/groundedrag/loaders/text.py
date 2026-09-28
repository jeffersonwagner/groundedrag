"""Plain-text / Markdown document loader."""

from __future__ import annotations

from pathlib import Path

from groundedrag.chunking import chunk_text
from groundedrag.schemas import Chunk, Document


def load_text(
    path: str | Path,
    *,
    chunk_size: int = 800,
    overlap: int = 100,
) -> tuple[Document, list[Chunk]]:
    """Load a plain-text or Markdown file into a Document and its Chunks."""
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    document_id = file_path.stem
    document = Document(id=document_id, source=str(file_path))
    chunks = [
        Chunk(id=f"{document_id}::{i}", document_id=document_id, text=piece)
        for i, piece in enumerate(chunk_text(text, chunk_size=chunk_size, overlap=overlap))
    ]
    return document, chunks
