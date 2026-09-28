"""Post-generation citation verification.

A prompt asking the LLM to cite ``[n]`` per claim is an instruction, not a
guarantee. This module turns "we asked it to cite" into "we checked that it
did" — see docs/architecture.md.
"""

from __future__ import annotations

import re

from groundedrag.schemas import Answer, Citation

_CITATION_RE = re.compile(r"\[(\d+)]")


def extract_citations(text: str, retrieved_chunk_ids: list[str]) -> list[Citation]:
    """Extract every ``[n]`` citation in ``text`` and check it against
    ``retrieved_chunk_ids`` (1-indexed, in retrieval order).

    A citation index outside the retrieved range is marked invalid rather
    than dropped, so the caller can decide how to surface it.
    """
    citations: list[Citation] = []
    for match in _CITATION_RE.finditer(text):
        index = int(match.group(1))
        in_range = 1 <= index <= len(retrieved_chunk_ids)
        citations.append(
            Citation(
                index=index,
                chunk_id=retrieved_chunk_ids[index - 1] if in_range else None,
                valid=in_range,
            )
        )
    return citations


def is_fully_cited(text: str, citations: list[Citation]) -> bool:
    """Return True only if every citation found in ``text`` is valid.

    An answer with zero citations is not "fully cited" — the caller decides
    whether that is acceptable (e.g. a refusal message needs none).
    """
    if not citations:
        return False
    return all(c.valid for c in citations)


def build_answer(text: str, retrieved_chunk_ids: list[str]) -> Answer:
    """Run the full guardrail pass and return a checked :class:`Answer`.

    This is the function callers should reach for after generation: it
    extracts and verifies citations in one step, so an unverified LLM
    response never accidentally reaches the caller as if it were checked.
    """
    citations = extract_citations(text, retrieved_chunk_ids)
    return Answer(text=text, citations=citations, fully_cited=is_fully_cited(text, citations))
