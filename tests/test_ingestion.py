"""Tests for the directory-walking ingestion helper."""

import pytest

from groundedrag.ingestion import load_directory


def test_loads_txt_and_md_files(tmp_path):
    (tmp_path / "policy.md").write_text("Employees may work remotely.")
    (tmp_path / "manual.txt").write_text("Reset the pump before reassembly.")
    (tmp_path / "ignored.json").write_text("{}")

    documents, chunks = load_directory(tmp_path)

    assert {d.id for d in documents} == {"policy", "manual"}
    assert {c.document_id for c in chunks} == {"policy", "manual"}


def test_ignores_subdirectories(tmp_path):
    (tmp_path / "policy.md").write_text("Top-level document.")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "other.md").write_text("Nested document, not loaded.")

    documents, _ = load_directory(tmp_path)

    assert [d.id for d in documents] == ["policy"]


def test_non_directory_raises():
    with pytest.raises(NotADirectoryError):
        load_directory("/path/does/not/exist")
