"""Anthropic implementation of LLMProvider."""

from __future__ import annotations


class AnthropicProvider:
    """Calls the Anthropic Messages API. Requires the ``anthropic`` extra."""

    def __init__(self, model: str = "claude-haiku-4-5", api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
            except ImportError as exc:
                raise ImportError(
                    "AnthropicProvider requires the 'anthropic' package. "
                    "Install it with: pip install groundedrag[anthropic]"
                ) from exc
            self._client = anthropic.Anthropic(api_key=self.api_key)
        return self._client

    def generate(self, prompt: str, *, temperature: float = 0.1) -> str:
        client = self._get_client()
        response = client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
            # `temperature` was dropped from the typed `messages.create()`
            # signature in recent SDK versions (verified against the
            # installed 1.7.0: passing it directly raises a TypeError), but
            # the API still accepts it as a body field via `extra_body`.
            extra_body={"temperature": temperature},
        )
        return "".join(block.text for block in response.content if block.type == "text")
