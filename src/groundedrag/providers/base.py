"""The LLMProvider interface every generation backend implements.

groundedrag's core never imports a vendor SDK directly — it only depends on
this Protocol, so swapping providers never touches gate.py or
guardrails.py (see docs/adr/0001-domain-agnostic-core.md).
"""

from __future__ import annotations

from typing import Protocol


class LLMProvider(Protocol):
    """Minimal surface groundedrag needs from any LLM backend."""

    def generate(self, prompt: str, *, temperature: float = 0.1) -> str:
        """Return the model's completion for ``prompt``."""
        ...
