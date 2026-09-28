"""Plain-text chunking shared by every loader.

Kept dependency-free and separate from any single file format so it can be
unit-tested without a real PDF, DOCX, or OCR engine involved.
"""

from __future__ import annotations


def chunk_text(text: str, *, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Split ``text`` into overlapping chunks of at most ``chunk_size`` characters.

    Splits happen on whitespace boundaries where possible, so words are not
    cut in half at a chunk edge. ``overlap`` characters of context are
    repeated at the start of the next chunk, so a fact near a chunk
    boundary isn't lost from every chunk's context.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        if end < text_length:
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= text_length:
            break
        start = end - overlap

    return chunks
