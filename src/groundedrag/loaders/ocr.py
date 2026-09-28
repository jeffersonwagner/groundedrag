"""OCR for scanned pages, used by loaders/pdf.py as an automatic fallback.

Requires the ``ocr`` extra (``pytesseract`` + ``pdf2image``) and the
Tesseract and Poppler system binaries.
"""

from __future__ import annotations

from typing import Any


def ocr_image(image: Any, *, lang: str = "eng") -> str:
    """Run OCR on a single image (a PIL Image, as returned by pdf2image)."""
    try:
        import pytesseract
    except ImportError as exc:
        raise ImportError(
            "OCR requires the 'pytesseract' package and the Tesseract binary. "
            "Install the package with: pip install groundedrag[ocr]"
        ) from exc
    return pytesseract.image_to_string(image, lang=lang)
