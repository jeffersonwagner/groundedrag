"""Opt-in live smoke tests against the real vendor APIs — skipped unless
the matching credentials are present in the environment.

These exist because tests/test_providers.py mocks the SDK client, which
verifies groundedrag's request-building logic but not that the vendor's
*current* SDK still accepts that request — see docs/adr/0004, which was
written after exactly that kind of drift broke the Anthropic provider
silently past the mocked tests. Never run in default CI: no vendor
credentials are configured there. Run locally with the relevant API key
exported to catch this class of drift before a release.
"""

import os

import pytest

from groundedrag.providers.anthropic import AnthropicProvider
from groundedrag.providers.openai import OpenAIProvider

_PROMPT = "Reply with the single word: pong"


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"), reason="requires ANTHROPIC_API_KEY"
)
def test_anthropic_provider_live():
    provider = AnthropicProvider()
    result = provider.generate(_PROMPT, temperature=0.0)
    assert "pong" in result.lower()


@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="requires OPENAI_API_KEY")
def test_openai_provider_live():
    provider = OpenAIProvider()
    result = provider.generate(_PROMPT, temperature=0.0)
    assert "pong" in result.lower()
