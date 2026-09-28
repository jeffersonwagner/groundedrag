"""Walks a directory of source files into (Document, Chunk) pairs.

Kept separate from the CLI so it's testable without Typer, and separate
from the individual loaders so adding a new file type only means adding
one entry here.
"""

from __future__ import annotations

from pathlib import Path

from groundedrag.loaders.text import load_text
from groundedrag.schemas import Chunk, Document

_LOADERS_BY_SUFFIX = {".txt": load_text, ".md": load_text}


def load_directory(path: str | Path) -> tuple[list[Document], list[Chunk]]:
    """Load every supported file directly under ``path`` (non-recursive).

    ``.pdf`` is only dispatched if the ``pdf`` extra is installed — trying
    to ingest a PDF without it raises the same clear ``ImportError`` as
    calling ``load_pdf`` directly would.
    """
    directory = Path(path)
    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    documents: list[Document] = []
    chunks: list[Chunk] = []
    for file_path in sorted(directory.iterdir()):
        if not file_path.is_file():
            continue
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            from groundedrag.loaders.pdf import load_pdf

            document, file_chunks = load_pdf(file_path)
        elif suffix in _LOADERS_BY_SUFFIX:
            document, file_chunks = _LOADERS_BY_SUFFIX[suffix](file_path)
        else:
            continue
        documents.append(document)
        chunks.extend(file_chunks)

    return documents, chunks
