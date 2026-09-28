"""Core data contracts shared by every layer of groundedrag.

These types are intentionally domain-agnostic (see docs/adr/0001). Nothing
here should end up knowing what a "topic" means in any particular caller's
domain.
"""

from __future__ import annotations

from pydantic import BaseModel


class Document(BaseModel):
    """A single ingested source document."""

    id: str
    source: str
    topics: list[str] = []


class Chunk(BaseModel):
    """A retrievable slice of a Document, as produced by a loader."""

    id: str
    document_id: str
    text: str
    metadata: dict[str, str] = {}


class GateDecision(BaseModel):
    """The gate's verdict for a single question."""

    allowed: bool
    topic: str
    reason: str
    missing_documents_hint: str | None = None


class Citation(BaseModel):
    """A single [n] citation extracted from an LLM answer."""

    index: int
    chunk_id: str | None
    valid: bool


class Answer(BaseModel):
    """The final, guardrail-checked answer returned to the caller."""

    text: str
    citations: list[Citation] = []
    fully_cited: bool
