"""The Embedder interface every embedding backend implements."""

from __future__ import annotations

from typing import Protocol


class Embedder(Protocol):
    """Minimal surface groundedrag needs from any embedding backend."""

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text, in order."""
        ...
