"""Runnable demo: a compliance Q&A bot that only answers from policy
documents, with every claim cited back to a specific one.

Run with (from the repository root, after `uv sync`):

    uv run python examples/compliance_qa/demo.py

No API key needed — this demo runs entirely offline with the dependency-
free `HashingEmbedder` and shows groundedrag's two core guarantees:

1. A documented question retrieves real chunks from the indexed policy.
2. An undocumented question is refused *before* any LLM would be called —
   the exact behavior that matters most in a compliance context, where an
   invented answer is a liability, not just a bad user experience.

Set ANTHROPIC_API_KEY to also see a real, cited LLM answer for the
documented question.
"""

from __future__ import annotations

import os
from pathlib import Path

from groundedrag.coverage import CoverageMap
from groundedrag.embeddings.hashing import HashingEmbedder
from groundedrag.gate import DocumentGate
from groundedrag.guardrails import build_answer
from groundedrag.ingestion import load_directory
from groundedrag.prompting import build_prompt
from groundedrag.retriever import GatedRetriever
from groundedrag.stores.memory import InMemoryStore

DOCUMENTS_DIR = Path(__file__).parent / "documents"


def _print_header(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def _generate_cited_answer(retriever: GatedRetriever, topic: str, question: str) -> None:
    decision, chunks = retriever.retrieve(topic, question)
    if not decision.allowed:
        print(f"Refused: {decision.missing_documents_hint}")
        return

    prompt = build_prompt(question, chunks)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY to see a real, cited answer here.")
        print("The prompt that would be sent to the LLM:\n")
        print(prompt)
        return

    from groundedrag.providers.anthropic import AnthropicProvider

    raw_answer = AnthropicProvider().generate(prompt)
    answer = build_answer(raw_answer, [chunk.id for chunk in chunks])
    print(answer.text)
    print()
    print("Fully cited:", answer.fully_cited)


def main() -> None:
    documents, chunks = load_directory(DOCUMENTS_DIR)
    embedder = HashingEmbedder()
    vectors = embedder.embed([chunk.text for chunk in chunks])
    store = InMemoryStore()
    store.add(chunks, vectors)

    coverage = CoverageMap()
    coverage.add("data-retention", ["data_retention_policy"])
    coverage.add("access-control", ["access_control_policy"])
    retriever = GatedRetriever(DocumentGate(coverage), store, embedder)

    _print_header("1. Documented question — the gate allows retrieval")
    question = "How long are customer support tickets kept?"
    decision, retrieved = retriever.retrieve("data-retention", question)
    print(f"Question: {question}")
    print(f"Gate decision: allowed={decision.allowed}")
    for i, chunk in enumerate(retrieved, start=1):
        print(f"  [{i}] {chunk.text}")

    _print_header("2. Undocumented question — refused before any LLM call")
    question = "Can EU customers request full erasure under GDPR?"
    decision, retrieved = retriever.retrieve("gdpr-erasure-requests", question)
    print(f"Question: {question}")
    print(f"Gate decision: allowed={decision.allowed}")
    print(f"Refusal reason: {decision.missing_documents_hint}")
    print(
        "\nThis is the behavior that matters most in a compliance context: "
        "an invented answer about a data-subject right is a liability, not "
        "just a bad user experience."
    )

    _print_header("3. Generating a verified, cited answer")
    _generate_cited_answer(
        retriever, "data-retention", "How long are customer support tickets kept?"
    )


if __name__ == "__main__":
    main()
