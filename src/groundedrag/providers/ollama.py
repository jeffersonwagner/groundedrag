"""Local Ollama implementation of LLMProvider."""

from __future__ import annotations


class OllamaProvider:
    """Calls a local Ollama server. Requires the ``ollama`` extra."""

    def __init__(
        self,
        model: str = "qwen2.5:7b-instruct-q4_K_M",
        host: str = "http://localhost:11434",
    ) -> None:
        self.model = model
        self.host = host
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import ollama
            except ImportError as exc:
                raise ImportError(
                    "OllamaProvider requires the 'ollama' package. "
                    "Install it with: pip install groundedrag[ollama]"
                ) from exc
            self._client = ollama.Client(host=self.host)
        return self._client

    def generate(self, prompt: str, *, temperature: float = 0.1) -> str:
        client = self._get_client()
        response = client.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": temperature},
        )
        return response["response"]
