"""sentence-transformers implementation of Embedder (local, offline).

Default embedding backend — no API key required. Requires the
``sentence-transformers`` extra (pulls in PyTorch, which is a heavy
download — this is why it is optional rather than a base dependency).
"""

from __future__ import annotations


class SentenceTransformersEmbedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise ImportError(
                    "SentenceTransformersEmbedder requires the 'sentence-transformers' "
                    "package. Install it with: pip install groundedrag[sentence-transformers]"
                ) from exc
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        model = self._get_model()
        vectors = model.encode(texts, convert_to_numpy=True)
        return [vector.tolist() for vector in vectors]
