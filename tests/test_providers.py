"""Provider tests mock the vendor SDK client, so they run offline and never
hit a real API — they check that groundedrag builds the right request and
parses the response correctly, not that the vendor's API works."""

from types import SimpleNamespace

import pytest

from groundedrag.providers.anthropic import AnthropicProvider
from groundedrag.providers.ollama import OllamaProvider
from groundedrag.providers.openai import OpenAIProvider


def test_anthropic_provider_generate(monkeypatch):
    captured = {}

    class FakeMessages:
        def create(self, **kwargs):
            captured.update(kwargs)
            block = SimpleNamespace(type="text", text="Reset the password [1].")
            return SimpleNamespace(content=[block])

    class FakeClient:
        def __init__(self, api_key=None):
            captured["api_key"] = api_key
            self.messages = FakeMessages()

    fake_module = SimpleNamespace(Anthropic=FakeClient)
    monkeypatch.setitem(__import__("sys").modules, "anthropic", fake_module)

    provider = AnthropicProvider(model="claude-haiku-4-5", api_key="sk-test")
    result = provider.generate("What do I do?", temperature=0.2)

    assert result == "Reset the password [1]."
    assert captured["model"] == "claude-haiku-4-5"
    # temperature rides extra_body, not a direct kwarg — see provider docstring
    assert captured["extra_body"] == {"temperature": 0.2}
    assert captured["api_key"] == "sk-test"


def test_anthropic_provider_missing_dependency(monkeypatch):
    monkeypatch.setitem(__import__("sys").modules, "anthropic", None)
    provider = AnthropicProvider()
    with pytest.raises(ImportError, match="groundedrag\\[anthropic\\]"):
        provider.generate("hi")


def test_openai_provider_generate(monkeypatch):
    captured = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured.update(kwargs)
            message = SimpleNamespace(content="Reset the password [1].")
            return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    class FakeChat:
        def __init__(self):
            self.completions = FakeCompletions()

    class FakeClient:
        def __init__(self, api_key=None):
            captured["api_key"] = api_key
            self.chat = FakeChat()

    fake_module = SimpleNamespace(OpenAI=FakeClient)
    monkeypatch.setitem(__import__("sys").modules, "openai", fake_module)

    provider = OpenAIProvider(model="gpt-4o-mini", api_key="sk-test")
    result = provider.generate("What do I do?", temperature=0.2)

    assert result == "Reset the password [1]."
    assert captured["model"] == "gpt-4o-mini"
    assert captured["temperature"] == 0.2


def test_ollama_provider_generate(monkeypatch):
    captured = {}

    class FakeClient:
        def __init__(self, host=None):
            captured["host"] = host

        def generate(self, **kwargs):
            captured.update(kwargs)
            return {"response": "Reset the password [1]."}

    fake_module = SimpleNamespace(Client=FakeClient)
    monkeypatch.setitem(__import__("sys").modules, "ollama", fake_module)

    provider = OllamaProvider(model="qwen2.5:7b", host="http://localhost:11434")
    result = provider.generate("What do I do?", temperature=0.3)

    assert result == "Reset the password [1]."
    assert captured["host"] == "http://localhost:11434"
    assert captured["options"] == {"temperature": 0.3}
