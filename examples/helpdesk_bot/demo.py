"""Runnable demo: an internal IT helpdesk bot that refuses to answer
without documentation.

Run with (from the repository root, after `uv sync`):

    uv run python examples/helpdesk_bot/demo.py

No API key needed — this demo runs entirely offline with the dependency-
free `HashingEmbedder` and shows groundedrag's two core guarantees:

1. A documented question retrieves real chunks from the indexed policy.
2. An undocumented question is refused *before* any LLM would be called.

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
    print("Fully cited:" , answer.fully_cited)


def main() -> None:
    documents, chunks = load_directory(DOCUMENTS_DIR)
    embedder = HashingEmbedder()
    vectors = embedder.embed([chunk.text for chunk in chunks])
    store = InMemoryStore()
    store.add(chunks, vectors)

    coverage = CoverageMap()
    coverage.add("remote-work", ["remote_work_policy"])
    coverage.add("vpn-setup", ["vpn_setup"])
    retriever = GatedRetriever(DocumentGate(coverage), store, embedder)

    _print_header("1. Documented question — the gate allows retrieval")
    question = "How many days a week can I work remotely?"
    decision, retrieved = retriever.retrieve("remote-work", question)
    print(f"Question: {question}")
    print(f"Gate decision: allowed={decision.allowed}")
    for i, chunk in enumerate(retrieved, start=1):
        print(f"  [{i}] {chunk.text}")

    _print_header("2. Undocumented question — refused before any LLM call")
    question = "What's the reimbursement policy for home office equipment?"
    decision, retrieved = retriever.retrieve("home-office-budget", question)
    print(f"Question: {question}")
    print(f"Gate decision: allowed={decision.allowed}")
    print(f"Refusal reason: {decision.missing_documents_hint}")

    _print_header("3. Generating a verified, cited answer")
    _generate_cited_answer(
        retriever, "remote-work", "How many days a week can I work remotely?"
    )


if __name__ == "__main__":
    main()
