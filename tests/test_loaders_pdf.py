"""Tests for the PDF loader.

The native-extraction path is tested against a real PDF generated with
fpdf2 (a tiny, pure-Python dependency) — no OCR engine required. The OCR
fallback path is tested with `_ocr_page` mocked, so it doesn't require the
Tesseract/Poppler system binaries either.
"""

from fpdf import FPDF

from groundedrag.loaders import pdf as pdf_loader
from groundedrag.loaders.pdf import load_pdf


def _make_pdf(path, text: str) -> None:
    doc = FPDF()
    doc.add_page()
    doc.set_font("Helvetica", size=12)
    doc.cell(text=text)
    doc.output(str(path))


def test_load_pdf_extracts_native_text(tmp_path):
    path = tmp_path / "manual.pdf"
    _make_pdf(path, "Reset the pump before reassembly.")

    document, chunks = load_pdf(path)

    assert document.id == "manual"
    assert len(chunks) == 1
    assert "Reset the pump" in chunks[0].text
    assert chunks[0].metadata["ocr"] == "false"
    assert chunks[0].metadata["page"] == "1"


def test_load_pdf_falls_back_to_ocr_for_scanned_pages(tmp_path, monkeypatch):
    # A blank page has no extractable text, so it should trigger OCR.
    path = tmp_path / "scanned.pdf"
    doc = FPDF()
    doc.add_page()
    doc.output(str(path))

    monkeypatch.setattr(pdf_loader, "_ocr_page", lambda p, n, lang: "Scanned bearing manual.")

    document, chunks = load_pdf(path)

    assert len(chunks) == 1
    assert chunks[0].text == "Scanned bearing manual."
    assert chunks[0].metadata["ocr"] == "true"


def test_load_pdf_without_ocr_fallback_yields_no_chunks_for_blank_page(tmp_path):
    path = tmp_path / "blank.pdf"
    doc = FPDF()
    doc.add_page()
    doc.output(str(path))

    _, chunks = load_pdf(path, ocr_fallback=False)

    assert chunks == []
