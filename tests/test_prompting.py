"""Tests for the prompt builder."""

from groundedrag.prompting import build_prompt
from groundedrag.schemas import Chunk


def test_prompt_numbers_chunks_from_one():
    chunks = [
        Chunk(id="a", document_id="doc-1", text="Reset the pump."),
        Chunk(id="b", document_id="doc-1", text="Notify the supervisor."),
    ]

    prompt = build_prompt("What do I do?", chunks)

    assert "[1] Reset the pump." in prompt
    assert "[2] Notify the supervisor." in prompt
    assert "What do I do?" in prompt
    assert "[n]" in prompt or "square" in prompt  # citation instruction present


def test_prompt_with_no_chunks_still_has_instructions_and_question():
    prompt = build_prompt("What do I do?", [])
    assert "What do I do?" in prompt
    assert "Context:" in prompt
