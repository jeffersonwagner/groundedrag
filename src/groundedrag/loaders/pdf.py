"""PDF document loader, with automatic OCR fallback (see loaders/ocr.py).

A scanned PDF has no extractable text layer; falling back to OCR
automatically — rather than as a manual step someone has to remember to
run — avoids the silent failure of a scanned document quietly never
getting indexed. Requires the ``pdf`` extra (``pypdf``); the OCR fallback
additionally requires the ``ocr`` extra.
"""

from __future__ import annotations

from pathlib import Path

from groundedrag.chunking import chunk_text
from groundedrag.loaders.ocr import ocr_image
from groundedrag.schemas import Chunk, Document

DEFAULT_MIN_NATIVE_CHARS = 20


def load_pdf(
    path: str | Path,
    *,
    ocr_fallback: bool = True,
    min_native_chars: int = DEFAULT_MIN_NATIVE_CHARS,
    chunk_size: int = 800,
    overlap: int = 100,
    ocr_lang: str = "eng",
) -> tuple[Document, list[Chunk]]:
    """Load a PDF, falling back to OCR per page when native extraction comes
    up short (fewer than ``min_native_chars`` characters)."""
    try:
        import pypdf
    except ImportError as exc:
        raise ImportError(
            "load_pdf requires the 'pypdf' package. Install it with: pip install groundedrag[pdf]"
        ) from exc

    file_path = Path(path)
    document_id = file_path.stem
    document = Document(id=document_id, source=str(file_path))

    reader = pypdf.PdfReader(str(file_path))
    chunks: list[Chunk] = []
    chunk_index = 0
    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        used_ocr = False
        if len(text) < min_native_chars and ocr_fallback:
            text = _ocr_page(file_path, page_number, lang=ocr_lang).strip()
            used_ocr = True
        for piece in chunk_text(text, chunk_size=chunk_size, overlap=overlap):
            chunks.append(
                Chunk(
                    id=f"{document_id}::{chunk_index}",
                    document_id=document_id,
                    text=piece,
                    metadata={"page": str(page_number), "ocr": str(used_ocr).lower()},
                )
            )
            chunk_index += 1

    return document, chunks


def _ocr_page(path: Path, page_number: int, *, lang: str) -> str:
    try:
        from pdf2image import convert_from_path
    except ImportError as exc:
        raise ImportError(
            "OCR fallback requires the 'pdf2image' package and the Poppler "
            "binaries. Install the package with: pip install groundedrag[ocr]"
        ) from exc
    images = convert_from_path(str(path), first_page=page_number, last_page=page_number)
    if not images:
        return ""
    return ocr_image(images[0], lang=lang)
