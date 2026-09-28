"""A dependency-free, deterministic embedder for demos and tests.

Not recommended for production retrieval quality — it's a simple hashed
bag-of-words vectorizer (the "hashing trick"), included so the examples
and the CLI's default configuration can run instantly with no API key, no
GPU, and no network access. Use ``OpenAIEmbedder`` or
``SentenceTransformersEmbedder`` for real retrieval quality.
"""

from __future__ import annotations

import hashlib
import math
import re

_WORD_RE = re.compile(r"[a-z0-9]+")


class HashingEmbedder:
    """Hashes each word into one of ``dimensions`` buckets with a random
    sign, then L2-normalizes. Same idea as scikit-learn's HashingVectorizer,
    reimplemented here to avoid pulling in a dependency for a demo-only
    backend."""

    def __init__(self, dimensions: int = 256) -> None:
        self.dimensions = dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for word in _WORD_RE.findall(text.lower()):
            digest = hashlib.sha256(word.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(v * v for v in vector))
        if norm == 0:
            return vector
        return [v / norm for v in vector]
