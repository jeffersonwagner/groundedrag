"""OpenAI implementation of Embedder. Requires the ``openai`` extra."""

from __future__ import annotations


class OpenAIEmbedder:
    def __init__(self, model: str = "text-embedding-3-small", api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import openai
            except ImportError as exc:
                raise ImportError(
                    "OpenAIEmbedder requires the 'openai' package. "
                    "Install it with: pip install groundedrag[openai]"
                ) from exc
            self._client = openai.OpenAI(api_key=self.api_key)
        return self._client

    def embed(self, texts: list[str]) -> list[list[float]]:
        client = self._get_client()
        response = client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]
