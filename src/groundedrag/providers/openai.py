"""OpenAI implementation of LLMProvider."""

from __future__ import annotations


class OpenAIProvider:
    """Calls the OpenAI chat completions API. Requires the ``openai`` extra."""

    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import openai
            except ImportError as exc:
                raise ImportError(
                    "OpenAIProvider requires the 'openai' package. "
                    "Install it with: pip install groundedrag[openai]"
                ) from exc
            self._client = openai.OpenAI(api_key=self.api_key)
        return self._client

    def generate(self, prompt: str, *, temperature: float = 0.1) -> str:
        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""
