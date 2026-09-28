"""Hallucination-rate benchmark: what happens to an out-of-scope question
with and without the documentary gate.

Run with (from the repository root, after `uv sync`):

    uv run python scripts/benchmark.py

Offline by default — no API key needed. It measures the one thing that's
objectively countable without judging answer quality: on questions with NO
matching documentation, how often does each pipeline produce an answer
anyway, instead of refusing?

    naive pipeline   (no gate): always retrieves the closest chunk it has
                                 and always calls the LLM from it, however
                                 unrelated that chunk actually is
    groundedrag pipeline (gated): refuses before ever calling the LLM when
                                 coverage is missing

Set ANTHROPIC_API_KEY to also see one live example of what the naive
pipeline's LLM actually says when generated from unrelated context.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from groundedrag.coverage import CoverageMap
from groundedrag.embeddings.hashing import HashingEmbedder
from groundedrag.gate import DocumentGate
from groundedrag.prompting import build_prompt
from groundedrag.retriever import GatedRetriever
from groundedrag.schemas import Chunk
from groundedrag.stores.memory import InMemoryStore

DOCUMENTED_TOPIC = "remote-work"
DOCUMENTED_DOCUMENT_ID = "remote_work_policy"
DOCUMENTED_TEXT = (
    "Employees may work remotely up to three days per week, subject to manager approval."
)

# Questions with no matching documentation at all — the case that matters.
OUT_OF_SCOPE_QUESTIONS = [
    "What's the reimbursement policy for home office equipment?",
    "Can I expense a conference ticket without pre-approval?",
    "What's the process for requesting a sabbatical?",
    "Are pets allowed in the office?",
    "How is overtime calculated for hourly contractors?",
]


@dataclass
class Result:
    question: str
    naive_chunk_text: str  # what an un-gated pipeline would answer from anyway
    gated_answered: bool


def _build_pipeline() -> tuple[GatedRetriever, InMemoryStore, HashingEmbedder]:
    embedder = HashingEmbedder()
    chunk = Chunk(
        id=f"{DOCUMENTED_DOCUMENT_ID}::0",
        document_id=DOCUMENTED_DOCUMENT_ID,
        text=DOCUMENTED_TEXT,
    )
    store = InMemoryStore()
    store.add([chunk], embedder.embed([chunk.text]))

    coverage = CoverageMap()
    coverage.add(DOCUMENTED_TOPIC, [DOCUMENTED_DOCUMENT_ID])
    retriever = GatedRetriever(DocumentGate(coverage), store, embedder)
    return retriever, store, embedder


def run() -> list[Result]:
    retriever, store, embedder = _build_pipeline()
    results = []
    for question in OUT_OF_SCOPE_QUESTIONS:
        # A naive pipeline has no coverage map to consult — it just runs an
        # unfiltered similarity search and generates from whatever comes
        # back, however unrelated. There's only one chunk in this index, so
        # that's what it gets every time, regardless of the question.
        [naive_chunk] = store.query(embedder.embed([question])[0], top_k=1)

        # The gate is asked about a topic no document was ever mapped to —
        # standing in for "this question doesn't match anything documented".
        decision, _ = retriever.retrieve("undocumented-topic", question)

        results.append(
            Result(
                question=question,
                naive_chunk_text=naive_chunk.text,
                gated_answered=decision.allowed,
            )
        )
    return results


def _print_report(results: list[Result]) -> None:
    naive_rate = 1.0  # a naive pipeline answers unconditionally, by construction
    gated_rate = sum(r.gated_answered for r in results) / len(results)

    print(f"{len(results)} out-of-scope questions (no matching documentation)\n")
    for r in results:
        print(f"Q: {r.question}")
        print(f'  naive pipeline would answer from: "{r.naive_chunk_text[:70]}..."')
        print(f"  groundedrag: {'answers (bug!)' if r.gated_answered else 'refuses'}")
        print()

    print(f"Naive pipeline answer rate on out-of-scope questions: {naive_rate:.0%}")
    print(f"groundedrag answer rate on out-of-scope questions:       {gated_rate:.0%}")
    print()
    print(
        "A pipeline with no gate has no way to know a question falls outside "
        "its documentation — it retrieves the closest chunk it has and "
        "generates from it regardless of relevance. groundedrag's coverage "
        "check happens before that call, so the LLM never gets the chance "
        "to fabricate an answer to fill the gap."
    )


def _print_live_example() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "\nSet ANTHROPIC_API_KEY to see a live example of what a naive, "
            "un-gated pipeline's LLM actually says when generated from "
            "unrelated context."
        )
        return

    from groundedrag.providers.anthropic import AnthropicProvider

    question = OUT_OF_SCOPE_QUESTIONS[0]
    unrelated_chunk = Chunk(
        id=f"{DOCUMENTED_DOCUMENT_ID}::0", document_id=DOCUMENTED_DOCUMENT_ID, text=DOCUMENTED_TEXT
    )
    naive_prompt = build_prompt(question, [unrelated_chunk]).replace(
        "If the context does not contain the answer, say so explicitly instead of guessing.",
        "Answer directly and confidently based on the context.",
    )
    answer = AnthropicProvider().generate(naive_prompt)
    print("\nLive example — naive pipeline's actual answer, generated from unrelated context:\n")
    print(f"Question: {question}")
    print(f'Context given: "{DOCUMENTED_TEXT}"')
    print(f"Answer: {answer}")


if __name__ == "__main__":
    benchmark_results = run()
    _print_report(benchmark_results)
    _print_live_example()
