"""The documentary gate: decides whether the LLM may be called at all.

This is the core of groundedrag (see docs/adr/0001-domain-agnostic-core.md).
"""

from __future__ import annotations

from groundedrag.coverage import CoverageMap
from groundedrag.schemas import GateDecision


class DocumentGate:
    """Refuses to let a question through to the LLM without coverage."""

    def __init__(self, coverage: CoverageMap) -> None:
        self.coverage = coverage

    def check(self, topic: str) -> GateDecision:
        """Return a GateDecision for ``topic``.

        When coverage is missing, ``allowed`` is False and
        ``missing_documents_hint`` explains what to add — the caller's LLM
        must never be invoked for a refused topic.
        """
        if self.coverage.has_coverage(topic):
            return GateDecision(allowed=True, topic=topic, reason="documented")
        return GateDecision(
            allowed=False,
            topic=topic,
            reason="no_documentation",
            missing_documents_hint=(
                f"No document is mapped to topic '{topic}'. "
                "Add one to the coverage map to enable answers on this topic."
            ),
        )
