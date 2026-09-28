"""Embedding backend tests. OpenAI is mocked (no network); sentence-
transformers is only checked for a clean ImportError message, since
actually running it would require downloading PyTorch."""

from types import SimpleNamespace

import pytest

from groundedrag.embeddings.openai import OpenAIEmbedder
from groundedrag.embeddings.sentence_transformers import SentenceTransformersEmbedder


def test_openai_embedder(monkeypatch):
    captured = {}

    class FakeEmbeddings:
        def create(self, **kwargs):
            captured.update(kwargs)
            data = [SimpleNamespace(embedding=[0.1, 0.2]) for _ in kwargs["input"]]
            return SimpleNamespace(data=data)

    class FakeClient:
        def __init__(self, api_key=None):
            captured["api_key"] = api_key
            self.embeddings = FakeEmbeddings()

    fake_module = SimpleNamespace(OpenAI=FakeClient)
    monkeypatch.setitem(__import__("sys").modules, "openai", fake_module)

    embedder = OpenAIEmbedder(model="text-embedding-3-small", api_key="sk-test")
    vectors = embedder.embed(["hello", "world"])

    assert vectors == [[0.1, 0.2], [0.1, 0.2]]
    assert captured["model"] == "text-embedding-3-small"
    assert captured["input"] == ["hello", "world"]


def test_sentence_transformers_embedder_missing_dependency(monkeypatch):
    monkeypatch.setitem(__import__("sys").modules, "sentence_transformers", None)
    embedder = SentenceTransformersEmbedder()
    with pytest.raises(ImportError, match="groundedrag\\[sentence-transformers\\]"):
        embedder.embed(["hello"])
