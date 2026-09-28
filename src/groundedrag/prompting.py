"""Builds the prompt sent to the LLM once the gate has allowed a question.

Kept separate from the providers so any prompt experiment doesn't touch
provider code, and so it's easy to unit test on its own.
"""

from __future__ import annotations

from groundedrag.schemas import Chunk

_INSTRUCTIONS = (
    "Answer the question using ONLY the numbered context below. "
    "Cite the source of every factual claim with its number in square "
    "brackets, like [1]. If the context does not contain the answer, say "
    "so explicitly instead of guessing."
)


def build_prompt(question: str, chunks: list[Chunk]) -> str:
    """Build a citation-required prompt from the retrieved ``chunks``.

    Chunks are numbered in retrieval order, 1-indexed — this numbering is
    exactly what ``groundedrag.guardrails.build_answer`` expects when it later
    checks each ``[n]`` citation against ``chunks[n - 1]``.
    """
    context = "\n\n".join(f"[{i}] {chunk.text}" for i, chunk in enumerate(chunks, start=1))
    return f"{_INSTRUCTIONS}\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"
