# Example: internal IT helpdesk bot

Two tiny policy documents (`documents/`) and a self-contained script
showing groundedrag's two core guarantees end to end — no API key or vector
database required.

```bash
uv sync --extra dev  # from the repository root, if you haven't already
uv run python examples/helpdesk_bot/demo.py
```

Set `ANTHROPIC_API_KEY` first to also see a real, cited LLM answer for the
documented question — otherwise the demo prints the prompt that would
have been sent.
